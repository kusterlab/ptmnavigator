import werkzeug.datastructures
import re
import datetime
import csv
import tomllib
import pandas as pd
import numpy as np
from typing import Literal

from . import constants, db_utils


# TODO: Type hints


def check_essential_columns(input_columns, datasetOmics, datasetType):
    # Regulation always needs to be in there
    if 'Regulation' not in input_columns:
        db_utils.throw_error("'Regulation' column is missing!")
    if 'Gene Names' not in input_columns and 'Uniprot' not in input_columns:
        db_utils.throw_error("Either 'Gene Names' or 'Uniprot' must be present!")
    if datasetOmics in constants.ptm_omics:
        if 'Modified sequence' not in input_columns and 'Psite' not in input_columns:
            db_utils.throw_error("Either 'Modified sequence' or 'Psite' must be present for PTM Datasets!")
    if datasetType == 'Curve':
        for curvecol in ['pEC50', 'Slope', 'Front', 'Back', 'Fold Change']:
            if curvecol not in input_columns:
                db_utils.throw_error(f"'{curvecol}' must be present for Curve Datasets!")


def insert_to_user_dataset_table(args, user_id):
    with db_utils.get_db_connection() as conn:
        conn.execute('INSERT INTO USER_DATASET(NAME, USER_ID, DATASET_TYPE, OMICS, TAXCODE) VALUES (?,?,?,?,?)',
                     [args.get('datasetName'), user_id, args.get('datasetType'), args.get('omics'),
                      args.get('taxcode')])
        dataset_id = conn.execute('SELECT MAX(UD.DATASET_ID) FROM USER_DATASET UD WHERE UD.USER_ID = ? AND UD.NAME = ?',
                                  [user_id, args.get('datasetName')]
                                  ).fetchall()[0][0]
        return dataset_id


def get_delimiter(csvfile: werkzeug.datastructures.FileStorage, nbytes=50000):
    sniffer = csv.Sniffer()
    data = csvfile.read(nbytes).decode('utf-8')
    delimiter = sniffer.sniff(data).delimiter
    # Reset the file reader
    csvfile.seek(0)
    return delimiter


def get_modification_symbol_to_id():
    with db_utils.get_db_connection() as conn:
        res = conn.execute('SELECT SYMBOL, MODIFICATION_ID FROM MODIFICATION').fetchall()
        return {symbol: modification_id for symbol, modification_id in res}


def clean_regulation(raw_regulation_val):
    if pd.isna(raw_regulation_val):
        return None
    # It is odd to have regulation_variants_lookup in a different place than the one method that makes use of it.
    # Think about how this could nicely be refactored. Maybe put all cleaning functions in one script
    res = constants.regulation_variants_lookup.get(raw_regulation_val, -1)
    if res != -1:
        return res
    else:
        db_utils.throw_error(f'Unrecognized regulation category: {raw_regulation_val}')
        return


def clean_sequence(seq):
    """Sometimes a peptides sequence is repeated with ";" or "," in between. In that case we only keep the first one"""
    return re.split('[;,]', seq)[0]


def clean_protein_id(row):
    if pd.notna(row['PROTEIN_ID_FROM_UNIPROT']):
        return row['PROTEIN_ID_FROM_UNIPROT']
    elif pd.notna(row['PROTEIN_ID_FROM_GENE_NAME']):
        return row['PROTEIN_ID_FROM_GENE_NAME']
    else:
        return None


def extract_modified_sites(row):
    res = []
    position_wo_mods = 0
    i = 0
    while i < len(row['Modified sequence']):
        if row['Modified sequence'][i] == '(':
            if i > 0:
                res.append(
                    f"{row['UNIPROT_ACC']}_{row['Modified sequence'][i - 1]}{position_wo_mods - 1 + row['START_POSITION']}")
                # Skip everything until closing parenthesis
                while i < len(row['Modified sequence']) and row['Modified sequence'][i] != ')':
                    i += 1
        else:
            position_wo_mods += 1
        i += 1
    return res


def create_colnames_variants_lookup_map(dataset_type: Literal['Curve', 'FoldChange']):
    if dataset_type == 'Curve':
        return {val: key
                for key, vals in
                list(constants.expected_colnames_fcdata_map.items()) + list(
                    constants.additional_expected_colnames_curve_map.items())
                for val in vals}
    else:
        return {val: key for key, vals in constants.expected_colnames_fcdata_map.items() for val in vals}


def map_colnames(colnames, variants_lookup):
    detail_columns = []
    actual_colnames_to_expected_colnames = {}
    for col in colnames:
        expected_colname_for_actual_colname = variants_lookup.get(col.lower().replace(' ', ''))
        if expected_colname_for_actual_colname:
            actual_colnames_to_expected_colnames[col] = expected_colname_for_actual_colname
        else:
            detail_columns.append(col)
    return actual_colnames_to_expected_colnames, detail_columns


def get_proteins_from_database(taxcode):
    with db_utils.get_db_connection() as conn:
        return pd.read_sql('SELECT PROTEIN_ID, GENE_NAME, UNIPROT_ACC FROM PROTEIN WHERE TAXCODE = ?',
                           conn,
                           params=[taxcode])


def retrieve_protein_ids_for_dataset(input_protein_df, database_protein_df):
    if 'Uniprot' in input_protein_df:
        uniprot_splits = input_protein_df[['Uniprot']].dropna().copy()
        uniprot_splits = pd.DataFrame(uniprot_splits['Uniprot'].apply(lambda s: re.split('[;,]', s)).explode())
        uniprot_splits = uniprot_splits.reset_index().merge(
            database_protein_df[['PROTEIN_ID', 'UNIPROT_ACC']].dropna(),
            left_on='Uniprot',
            right_on='UNIPROT_ACC',
            how='left'
        ).dropna(
        ).drop(['Uniprot', 'UNIPROT_ACC'], axis=1
               ).rename({'PROTEIN_ID': 'PROTEIN_ID_FROM_UNIPROT'},
                        axis=1)
        # To resolve ambiguities, group by row index and retain only the smallest protein id
        # (since canonical proteins were inserted first, this should be the 'most canonical' isoform possible)
        unique_mapped_proteins_after_uniprot = uniprot_splits.groupby('index').agg('min')
        input_protein_df = input_protein_df.merge(unique_mapped_proteins_after_uniprot,
                                                  left_index=True,
                                                  right_index=True,
                                                  how="left")
        unmapped_proteins = input_protein_df[pd.isna(input_protein_df['PROTEIN_ID_FROM_UNIPROT'])]
    else:
        unmapped_proteins = input_protein_df
    if 'Gene Names' in input_protein_df:
        unmapped_proteins = unmapped_proteins[['Gene Names']].dropna().copy()
        unmapped_proteins['Gene Name'] = unmapped_proteins['Gene Names'].apply(
            lambda s: re.split('[;,]', s)).explode()
        mapped_proteins_after_genename = unmapped_proteins.reset_index(
        ).merge(database_protein_df[['PROTEIN_ID', 'GENE_NAME']].dropna(),
                left_on='Gene Name',
                right_on='GENE_NAME',
                how='left'
                ).drop(['Gene Name', 'GENE_NAME', 'Gene Names'], axis=1
                       ).rename({'PROTEIN_ID': 'PROTEIN_ID_FROM_GENE_NAME'},
                                axis=1).dropna()
        # To resolve ambiguities, group by row index and retain only the smallest protein id
        # (since canonical proteins were inserted first, this should be the most canonical isoform possible)
        unique_mapped_proteins_after_genename = mapped_proteins_after_genename.groupby('index').agg('min')
        input_protein_df = input_protein_df.merge(
            unique_mapped_proteins_after_genename,
            left_index=True,
            right_index=True,
            how='left')
    # Combine the Uniprot and Gene Name based mappings - Uniprot gets priority
    # (Gene Name df only saw the rows that could not be mapped via Uniprot)
    if 'PROTEIN_ID_FROM_UNIPROT' in input_protein_df and 'PROTEIN_ID_FROM_GENE_NAME' in input_protein_df:
        input_protein_df['PROTEIN_ID'] = input_protein_df.apply(clean_protein_id, axis=1).astype('Int64')
        input_protein_df.drop(['PROTEIN_ID_FROM_UNIPROT', 'PROTEIN_ID_FROM_GENE_NAME'], axis=1, inplace=True)
    elif 'PROTEIN_ID_FROM_UNIPROT' in input_protein_df:
        input_protein_df.rename({'PROTEIN_ID_FROM_UNIPROT': 'PROTEIN_ID'}, axis=1, inplace=True)
    elif 'PROTEIN_ID_FROM_GENE_NAME' in input_protein_df:
        input_protein_df.rename({'PROTEIN_ID_FROM_GENE_NAME': 'PROTEIN_ID'}, axis=1, inplace=True)
    return input_protein_df['PROTEIN_ID']


def retrieve_peptide_ids_for_dataset(df):
    # Create a temporary table - Make sure the name is unique in case of concurrent inserts
    seq_temp_table_name = f"temp_seq_{int(datetime.datetime.now().timestamp())}"
    with db_utils.get_db_connection() as conn:
        df[['PROTEIN_ID', 'Sequence']].drop_duplicates().to_sql(
            seq_temp_table_name,
            conn,
            if_exists='replace')
        # Create an index - speeds the join up by 5-8 times
        conn.execute(f"CREATE INDEX idx_temp_seq ON {seq_temp_table_name}(Sequence)")
        seq_to_peptideid_df = pd.read_sql(
            f"""
            SELECT P.*, PTP.START_POSITION
            FROM {seq_temp_table_name} T
            JOIN PEPTIDE P ON P.SEQUENCE = T.Sequence
            JOIN PROTEIN_TO_PEPTIDE PTP ON P.PEPTIDE_ID = PTP.PEPTIDE_ID AND T.PROTEIN_ID = PTP.PROTEIN_ID
            ;
            """,
            conn)
        conn.execute(f"DROP TABLE {seq_temp_table_name}")
    return seq_to_peptideid_df.drop_duplicates()


def map_seq_to_peptide_ids(df):
    # Generate the unmodified sequence from the modified
    df['Sequence'] = df['Modified sequence'].apply(
        lambda modseq: re.sub('\\s*\\(.*?\\)\\s*', '', modseq))
    seq_to_peptide_id_df = retrieve_peptide_ids_for_dataset(df)

    df['Modified sequence'] = df['Modified sequence'].apply(clean_sequence)
    # We don't want to generate additional peptides for n terminal acetylation.
    # So we replace N-Terminal ACs by Ms.
    df['Modified sequence'] = df['Modified sequence'].apply(
        lambda seq: 'M' + seq[4:] if seq[0:4] == '(ac)' else seq)
    df = df.merge(
        seq_to_peptide_id_df,
        left_on='Sequence',
        right_on='SEQUENCE',
        how='left').drop(['Sequence', 'SEQUENCE'], axis=1)
    df['PEPTIDE_ID'] = df['PEPTIDE_ID'].astype('Int64')
    df['START_POSITION'] = df['START_POSITION'].astype('Int64')
    df = df[pd.notna(df['PEPTIDE_ID'])]
    df.reset_index(drop=True, inplace=True)
    return df


def find_and_log_transform_fold_changes(df):
    for col in df.columns:
        if col.lower().replace(' ', '') in ['foldchange', 'fc']:
            return np.log2(df[col])
    else:
        db_utils.throw_error('Trying to log-transform fold change column but could not find it!')


def construct_modsite_df(df):
    # Again, we create a temporary table to get the MODIFIED_SITE_IDs for these SITE_IDENTIFIERs
    modsite_temp_table_name = f"temp_modsite_{int(datetime.datetime.now().timestamp())}"
    with db_utils.get_db_connection() as conn:
        df[['SITE_IDENTIFIER']].dropna().drop_duplicates().to_sql(
            modsite_temp_table_name,
            conn,
            if_exists='replace')
        conn.execute(f"CREATE INDEX idx_temp_modsite ON {modsite_temp_table_name}(SITE_IDENTIFIER)")
        modsite_id_df = pd.read_sql(
            f"""
            SELECT M.MODIFIED_SITE_ID, M.SITE_IDENTIFIER
            FROM {modsite_temp_table_name} T
            JOIN MODIFIED_SITE M ON M.SITE_IDENTIFIER = T.SITE_IDENTIFIER
            ;
            """,
            conn)
        conn.execute(f"DROP TABLE {modsite_temp_table_name}")
    modsite_df = df.reset_index().merge(modsite_id_df, how='left')
    modsite_df.set_index('index', inplace=True)
    modsite_df['KEY'] = 'MODIFIED_SITE_ID'
    modsite_df.rename({'MODIFIED_SITE_ID': 'VALUE'}, axis=1, inplace=True)
    modsite_df['VALUE'] = modsite_df['VALUE'].astype('Int64')
    return modsite_df


def construct_modified_site_identifiers_with_sequence(df, protein_df):
    df = df.merge(protein_df[['PROTEIN_ID', 'UNIPROT_ACC']],
                  on='PROTEIN_ID',
                  how='left')
    df['SITE_IDENTIFIER'] = df.apply(extract_modified_sites, axis=1)
    df = df.explode('SITE_IDENTIFIER')
    # Now we again create a temporary table to get the MODIFIED_SITE_IDs for these SITE_IDENTIFIERs
    return construct_modsite_df(df)


def construct_modified_site_identifiers_with_psite(df):
    # We have Psite level data, so the modified site identifiers can be constructed directly
    df['SITE_IDENTIFIER'] = df.apply(lambda row: f"{row['Uniprot']}_{row['Psite']}", axis=1)
    # Now we again create a temporary table to get the MODIFIED_SITE_IDs for these SITE_IDENTIFIERs
    return construct_modsite_df(df)


def create_curve_dfs(input_df, tomlfile):
    toml_data = tomllib.load(tomlfile)
    for col in input_df.columns:
        if any(f'{col.lower().replace(" ", "")}'.startswith(expected) for expected in
               ['ratio', 'tmtratio', 'tmtchannelratio', 'lfqratio']):
            factor_col_prefix = " ".join(col.split()[:-1])
            break
    else:
        db_utils.throw_error('Failed to process curve data. Could not find ratio columns.')
    column_to_factor = {f"{factor_col_prefix} {exp}": "%.3g" % (fact * float(toml_data['dose_scale']))
                        for exp, fact in zip(toml_data['experiments'], toml_data['doses'])}
    curve_data_df = input_df[column_to_factor.keys()
    ].rename(column_to_factor, axis=1
             ).reset_index(
    ).melt(id_vars='index', var_name='FACTOR_VALUE', value_name='RESPONSE_VALUE'
           ).set_index('index')
    curve_data_df['FACTOR_NAME'] = "Dose"  # Hard coded for now, change once the toml file allows something else
    curve_data_df['FACTOR_UNIT'] = toml_data['dose_unit']

    existing_additional_curve_columns = list(
        set(constants.additional_expected_colnames_curve_map.keys()).intersection(input_df.columns))
    curve_details_df = input_df[existing_additional_curve_columns].stack().reset_index()
    curve_details_df.set_index('level_0', inplace=True)
    curve_details_df.columns = ['KEY', 'VALUE']
    return curve_data_df, curve_details_df


def insert_modsites_to_details_table(modsite_df, db_connection):
    modsite_df.reset_index(names='USER_DATUM_ID')[
        ['USER_DATUM_ID', 'KEY', 'VALUE']
    ].to_sql(
        'USER_DATUM_DETAIL',
        db_connection,
        if_exists='append',
        index=False)


def insert_details(details_df, db_connection):
    details_df.reset_index(names='USER_DATUM_ID').to_sql(
        'USER_DATUM_DETAIL',
        db_connection,
        if_exists='append',
        index=False)


def insert_curve_data_and_details(curve_data_df, curve_details_df, db_connection):
    curve_data_df.reset_index(names='USER_CURVE_ID').to_sql(
        'USER_CURVE_DATA',
        db_connection,
        if_exists='append',
        index=False)
    curve_details_df.reset_index(names='USER_DATUM_ID').to_sql(
        'USER_DATUM_DETAIL',
        db_connection,
        if_exists='append',
        index=False)


def insert_quant(quant_df, dataset_type, db_connection):
    columns_to_insert = ['USER_DATUM_ID', 'DATASET_ID', 'REGULATION', 'PROTEIN_ID', 'EXPERIMENT']

    if 'MODIFIED_SEQUENCE' in quant_df:
        columns_to_insert += ['MODIFIED_SEQUENCE', 'PEPTIDE_ID']

    if dataset_type == 'Curve':
        columns_to_insert.append('USER_CURVE_ID')

    quant_df[columns_to_insert].to_sql(
        'USER_QUANTIFICATION_DATA',
        db_connection,
        if_exists='append',
        index=False)


def check_required_arguments(request_arguments):
    for arg in constants.required_arguments_for_upload:
        if arg not in request_arguments:
            db_utils.throw_error(f'Argument missing from request: "{arg}"')


def main(put_request: werkzeug.Request):
    """The entrypoint. The only method that should be called externally.
    Could make the others private.
    Not sure if `main` is the best name but I did not want to call it again `upload_dataset`"""
    check_required_arguments(put_request.args)

    input_csv_df = pd.read_csv(put_request.files['csvFile'],
                               sep=get_delimiter(put_request.files['csvFile']))

    colnames_variants_lookup = create_colnames_variants_lookup_map(put_request.args.get('datasetType'))
    actual_colnames_to_expected_colnames, detail_columns = map_colnames(input_csv_df.columns, colnames_variants_lookup)
    input_csv_df.rename(actual_colnames_to_expected_colnames, axis=1, inplace=True)

    check_essential_columns(input_csv_df.columns, put_request.args.get('omics'), put_request.args.get('datasetType'))

    if put_request.args.get('datasetType') == 'Curve':
        detail_columns = list(set(detail_columns) - constants.curve_columns_not_imported)

    # TODO: Currently not utilized - needs to be implemented if you want other mods than Phospho
    # modification_symbol_to_id = get_modification_symbol_to_id()

    input_csv_df['Regulation'] = input_csv_df['Regulation'].apply(clean_regulation)

    # Map protein IDs
    protein_df = get_proteins_from_database(put_request.args.get('taxcode'))
    input_csv_df['PROTEIN_ID'] = retrieve_protein_ids_for_dataset(
        # Only hand over Uniprot and Gene Names columns, if they exist.
        input_csv_df[list({'Uniprot', 'Gene Names'}.intersection(input_csv_df.columns))],
        protein_df)

    if 'Modified sequence' in input_csv_df:
        # Different from the protein ids, we don't load the entire peptide table into memory, it is too large.
        # So instead we create a temporary table in sqlite and join into the peptide table
        input_csv_df = map_seq_to_peptide_ids(input_csv_df)

    if put_request.args.get('omics') in constants.ptm_omics and 'Psite' not in input_csv_df:
        # Construct modified site identifiers from sequences
        modsite_df = construct_modified_site_identifiers_with_sequence(
            input_csv_df[
                ['PROTEIN_ID', 'PEPTIDE_ID', 'START_POSITION', 'Modified sequence']].drop_duplicates().copy(),
            protein_df)
    elif 'Psite' in input_csv_df:
        modsite_df = construct_modified_site_identifiers_with_psite(input_csv_df[['Uniprot', 'Psite']])

    # Log-transform the fold changes, if requested
    if put_request.args.get('foldChangeDataFoldChangeScale') == 'raw':
        input_csv_df['Log Fold Change'] = find_and_log_transform_fold_changes(input_csv_df)
    # Else we trust that they are log transformed already and rename the column:
    input_csv_df.rename({'Fold Change': 'Log Fold Change'}, axis=1, inplace=True)
    # And make sure this column is part of the details
    if 'Log Fold Change' not in detail_columns:
        detail_columns.append('Log Fold Change')

    # Create the table row for the dataset, which gives us the dataset id that we can use for the other tables
    dataset_id = insert_to_user_dataset_table(put_request.args, db_utils.retrieve_user_id(put_request.args.get('uuid')))

    # Finalize the data frames for import
    input_csv_df['DATASET_ID'] = dataset_id
    # If no experiment IDs were supplied, reuse the datasetName
    if 'Experiment' not in input_csv_df:
        input_csv_df['Experiment'] = put_request.args.get('datasetName')

    # Create details data frame
    input_csv_df_detail = input_csv_df[detail_columns].stack().reset_index()
    input_csv_df_detail.set_index('level_0', inplace=True)
    input_csv_df_detail.columns = ['KEY', 'VALUE']

    # Additional processing for curve Data
    if put_request.args.get('datasetType') == 'Curve':
        curve_data_df, curve_details_df = create_curve_dfs(input_csv_df, put_request.files['tomlFile'])

    # Retrieve the next USER_DATUM_ID and, if we have Curve Data, USER_CURVE_ID
    with db_utils.get_db_connection() as conn:
        next_user_datum_id = conn.execute(
            'SELECT MAX(USER_DATUM_ID)+1 FROM USER_QUANTIFICATION_DATA').fetchall()[0][0] or 1
        if put_request.args.get('datasetType') == 'Curve':
            next_user_curve_id = conn.execute('SELECT MAX(USER_CURVE_ID)+1 FROM USER_CURVE_DATA').fetchall()[0][0] or 1

    # Offset the indices so that they can be used as IDs
    input_csv_df.index += next_user_datum_id
    input_csv_df_detail.index += next_user_datum_id
    if put_request.args.get('omics') in constants.ptm_omics:
        modsite_df.index += next_user_datum_id
    if put_request.args.get('datasetType') == 'Curve':
        input_csv_df['USER_CURVE_ID'] = range(next_user_curve_id, next_user_curve_id + len(input_csv_df))
        curve_details_df.index += next_user_datum_id
        curve_data_df.index += next_user_curve_id

    user_quantification_data_df = input_csv_df.reset_index().rename(
        {'index': 'USER_DATUM_ID', 'Experiment': 'EXPERIMENT',
         'Regulation': 'REGULATION', 'Modified sequence': 'MODIFIED_SEQUENCE'}, axis=1)

    # Insert everything
    with db_utils.get_db_connection() as conn:
        insert_quant(user_quantification_data_df, put_request.args.get('datasetType'), conn)
        if put_request.args.get('datasetType') == 'Curve':
            insert_curve_data_and_details(curve_data_df, curve_details_df, conn)
        insert_details(input_csv_df_detail, conn)
        if put_request.args.get('omics') in constants.ptm_omics:
            insert_modsites_to_details_table(modsite_df, conn)

    return dict(datasetId=dataset_id, message='Upload of dataset was successful!')
