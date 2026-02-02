
import sqlite3
from pathlib import Path
import re
import json
import pandas as pd
from dbml_sqlite import toSQLite

DB_FILE = Path('data/sqlite_backend.db')

ISOFORM_REGEX = re.compile(r' Isoform of ([A-Z0-9]+),')
GENE_NAME_REGEX = re.compile(r'GN=([A-Z0-9]+)')


def create_database_schema(conn):
    print('Creating Database Schema...')
    dbml_filepath = 'diagram.dbml'
    ddl_string = toSQLite(dbml_filepath)
    conn.executescript(ddl_string)
    print('Done.')


def populate_small_static_tables(conn):
    """
    This fills the following tables:
    ORGANISM, MODIFICATION, PROTEASE, OMIC, ENRICHMENT_TYPE, ENRICHMENT_TYPE_TO_OMIC, ENZYME_CLASS
    """
    print('Populating small static tables...')
    organism_df = pd.DataFrame({
        'TAXCODE': [9606, 10090],
        'NAME': ['Homo sapiens', 'Mus musculus']})
    organism_df.to_sql('ORGANISM', conn, if_exists='append', index=False)

    modification_df = pd.DataFrame({
        'MODIFICATION_ID': [1],
        'NAME': ['Phosphorylation'],
        'SYMBOL': ['(ph)'],
        'MODIFIABLE_RESIDUES': ['STY']
    })
    modification_df.to_sql('MODIFICATION', conn, if_exists='append', index=False)

    protease_df = pd.DataFrame({
        'PROTEASE_ID': [1],
        'NAME': ['Trypsin'],
        'CLEAVAGE_RULE': ['([KR])(?!P)']

    })
    protease_df.to_sql('PROTEASE', conn, if_exists='append', index=False)

    omic_df = pd.DataFrame({
        'OMIC_ID': [1, 2, 3],
        'NAME': ['Phosphorylation', 'Protein', 'Others']
    })
    omic_df.to_sql('OMIC', conn, if_exists='append', index=False)

    enrichment_type_df = pd.read_excel('resources/Enrichment_Types.xlsx')
    enrichment_type_df.to_sql('ENRICHMENT_TYPE', conn, if_exists='append', index=False)

    enrichment_type_to_omic_df = pd.DataFrame({
        'ENRICHMENT_TYPE_ID': [1, 2, 2, 2, 3, 3, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10],
        'OMIC_ID': [1, 1, 2, 3, 1, 2, 3, 1, 1, 1, 1, 1, 1, 1, 2, 3],
    })
    enrichment_type_to_omic_df.to_sql('ENRICHMENT_TYPE_TO_OMIC', conn, if_exists='append', index=False)

    enzyme_class_df = pd.DataFrame({
        'ENZYME_CLASS_ID': [1],
        'NAME': ['Kinase'],
    })
    enzyme_class_df.to_sql('ENZYME_CLASS', conn, if_exists='append', index=False)
    print('Done.')


def process_reference_proteomes(conn):
    """
    This fills the following tables:
    PROTEIN, PEPTIDE, PROTEIN_TO_PEPTIDE, MODIFIED_SITE
    """
    print('Processing reference proteomes...')
    organism_df = pd.read_sql_query('SELECT * FROM ORGANISM', conn)
    protease_df = pd.read_sql_query('SELECT * FROM PROTEASE', conn)
    modification_df = pd.read_sql_query('SELECT * FROM MODIFICATION', conn)
    current_protein_id = 1
    current_peptide_id = 1
    current_modified_site_id = 1
    peptides = {}
    # for taxcode in organism_df['TAXCODE']: #TODO: Rewrite loop so that peptide_df is inserted only once.
    #  You must insert peptide_df only once, not after every species, else the sqlite database thinks there is duplication
    # (You are already making sure that there is no actual duplication)
    # For now, limit to human.
    for taxcode in [9606]:  # organism_df['TAXCODE']:
        matching_files = list(Path('resources/').glob(f'uniprot_proteome_w_isoforms_{taxcode}*.fasta'))
        if len(matching_files) > 1:
            print(f'''More than one fasta files match! Ambiguous.
            The following files match: {[f.name for f in matching_files]} 
            ''')
        else:
            fasta_path = matching_files[0]
        # TODO: Same as above. Currently only works because you only have a single protease
        for protease_index, protease_id, cleavage_rule in protease_df[['PROTEASE_ID', 'CLEAVAGE_RULE']].itertuples():
            cleavage_rule_compiled = re.compile(cleavage_rule)
            # TODO: Same as above. Currently only works because you only have a single modification type
            for modification_index, modification_id, modifiable_residues in modification_df[
                ['MODIFICATION_ID', 'MODIFIABLE_RESIDUES']].itertuples():
                print(f'Digesting {fasta_path} with cleavage rule {cleavage_rule} and modification {modification_id}')
                proteins, peptides, protein_to_peptides, modified_sites, \
                current_protein_id, current_peptide_id, current_modified_site_id = digest_proteome(
                    fasta_path,
                    cleavage_rule_compiled,
                    modification_id,
                    modifiable_residues,
                    peptides,
                    current_protein_id,
                    current_peptide_id,
                    current_modified_site_id,
                    taxcode,
                    protease_id,
                    conn)
                print('Digestion complete, filling tables...')
                populate_large_static_tables(proteins, peptides, protein_to_peptides, modified_sites,
                                             taxcode, protease_id,
                                             conn)
                print('Tables filled.')
    print('Done')


def add_enzyme_substrate_relationships(conn):
    """
    This fills the following tables:
    PROTEIN, PEPTIDE, PROTEIN_TO_PEPTIDE, MODIFIED_SITE
    """
    print('Processing enzyme substrate relationships...')
    phosphositeplus_kin_sub_filepath = Path('resources/Kinase_Substrate_Dataset_20231219')
    kin_sub_df = pd.read_csv(phosphositeplus_kin_sub_filepath, sep='\t', skiprows=3)
    organism = 'human'  # TODO: Do it for mouse, too
    kin_sub_df = kin_sub_df[(kin_sub_df['KIN_ORGANISM'] == organism) & (kin_sub_df['SUB_ORGANISM'] == organism)]
    kin_sub_df['SITE_IDENTIFIER'] = kin_sub_df.apply(
        lambda row: f"{row['SUB_ACC_ID']}_{row['SUB_MOD_RSD']}", axis=1)
    protein_df = pd.read_sql('SELECT PROTEIN_ID, UNIPROT_ACC FROM PROTEIN', conn)
    modified_site_df = pd.read_sql('SELECT MODIFIED_SITE_ID, SITE_IDENTIFIER FROM MODIFIED_SITE', conn)
    enzyme_class_df = pd.read_sql('SELECT * FROM ENZYME_CLASS', conn)
    enzyme_class_id = enzyme_class_df.loc[0]['ENZYME_CLASS_ID']  # TODO: Add more enzyme classes
    kin_sub_df_mapped = kin_sub_df[['KIN_ACC_ID', 'SITE_IDENTIFIER']].merge(protein_df,
                                                                            left_on='KIN_ACC_ID',
                                                                            right_on='UNIPROT_ACC',
                                                                            how='inner'
                                                                            ).merge(modified_site_df,
                                                                                    on='SITE_IDENTIFIER', how='inner')
    kin_sub_df_mapped['ENZYME_CLASS_ID'] = enzyme_class_id
    kin_sub_df_mapped.rename({
        'PROTEIN_ID': 'ENZYME_PROTEIN_ID',
        'MODIFIED_SITE_ID': 'SUBSTRATE_SITE_ID'
    }, axis=1, inplace=True)
    kin_sub_df_mapped[['ENZYME_PROTEIN_ID', 'SUBSTRATE_SITE_ID', 'ENZYME_CLASS_ID']].to_sql(
        'ENZYME_SUBSTRATE_RELATIONSHIP', conn, if_exists='append', index=False)
    print('Done.')


def process_pathway_jsonfile(jsonfile, taxcode, database, pathway_index,
                             pathway_tuples, pathway_to_protein_tuples, gene_nodetype):
    with open(jsonfile, 'r') as infile:
        pathway_skeleton = json.load(infile)
    # This splits the 'path:' prefix away from KEGG pathways
    pathway_name = pathway_skeleton['pathway']['name'].split(':')[-1]
    pathway_title = pathway_skeleton['pathway']['title']
    pathway_n_genes = len(
        {",".join(sorted(node['geneNames']))
         for node in pathway_skeleton['nodes'] if node['type'] == gene_nodetype})
    # Pathways with 0 genes are not interesting for this tool, since no peptide will ever be mapped to them
    if pathway_n_genes == 0:
        return
    pathway_tuples.append(
        (pathway_name, pathway_title, taxcode, database, pathway_n_genes, json.dumps(pathway_skeleton)))
    for node in pathway_skeleton['nodes']:
        if node['type'] == gene_nodetype:
            for gene in node.get('geneNames') or []:
                if gene:
                    pathway_to_protein_tuples.append(
                        (pathway_index, node.get('id'), gene, 'GENE_SYMBOL', taxcode))
            for uniprotAccs in node.get('uniprotAccs') or []:
                if uniprotAccs:
                    pathway_to_protein_tuples.append(
                        (pathway_index, node.get('id'), uniprotAccs, 'UNIPROT', taxcode))


def populate_pathway_table(pathway_tuples, conn):
    pathway_df = pd.DataFrame(pathway_tuples,
                              columns=['PATHWAY_NAME', 'TITLE', 'TAXCODE', 'DATABASE', 'N_GENES', 'PATHWAY_JSON'])
    pathway_df.index.name = 'PATHWAY_ID'
    # SQL Tables are conventionally 1-indexed
    pathway_df.index += 1
    pathway_df.reset_index().to_sql('PATHWAY', conn, if_exists='append', index=False)


def populate_pathway_to_protein_table(pathway_to_protein_tuples, conn):
    pathway_to_protein_df = pd.DataFrame(pathway_to_protein_tuples,
                                         columns=['PATHWAY_ID', 'NODE_ID', 'GENE_IDENTIFIER', 'IDENTIFIER_TYPE',
                                                  'TAXCODE'])

    # Concatenate the NODE_IDs of identical genes into lists so that each gene identifier is unique in each pathway
    pathway_to_protein_df = pathway_to_protein_df.groupby(
        ['PATHWAY_ID', 'GENE_IDENTIFIER', 'IDENTIFIER_TYPE', 'TAXCODE']).agg(
        lambda node_ids: ",".join(list(node_ids))).reset_index()
    pathway_to_protein_df.rename({'NODE_ID': 'NODE_IDS'}, axis=1, inplace=True)

    protein_df = pd.read_sql('SELECT PROTEIN_ID, GENE_NAME, UNIPROT_ACC FROM PROTEIN', conn)
    pw2pr_genesymbol = pathway_to_protein_df[pathway_to_protein_df['IDENTIFIER_TYPE'] == 'GENE_SYMBOL'].merge(
        protein_df,
        left_on='GENE_IDENTIFIER',
        right_on='GENE_NAME',
        how='inner')[['PATHWAY_ID', 'NODE_IDS', 'PROTEIN_ID']]
    pw2pr_uniprot = pathway_to_protein_df[pathway_to_protein_df['IDENTIFIER_TYPE'] == 'UNIPROT'].merge(
        protein_df,
        left_on='GENE_IDENTIFIER',
        right_on='UNIPROT_ACC',
        how='inner')[['PATHWAY_ID', 'NODE_IDS', 'PROTEIN_ID']]
    pw2pr_concatenated = pd.concat([pw2pr_uniprot, pw2pr_genesymbol]).drop_duplicates()
    pw2pr_concatenated.to_sql('PATHWAY_TO_PROTEIN', conn, if_exists='append', index=False)


def import_canonical_pathways(conn):
    """
    This fills the following tables:
    PATHWAY, PATHWAY_TO_PROTEIN
    """
    print('Importing Canonical Pathways...')
    json_directory = Path('resources/wikipathways_jsons/')
    GENE_NODETYPE = 'gene_protein'
    database = 'wikipathways'
    pathway_tuples = []
    pathway_to_protein_tuples = []
    pathway_index = 1

    organism_df = pd.read_sql_query('SELECT * FROM ORGANISM', conn)
    for taxcode in organism_df['TAXCODE']:
        json_directory_organism = json_directory.joinpath(str(taxcode))
        for jsonfile in json_directory_organism.glob('*.json'):
            process_pathway_jsonfile(jsonfile, taxcode, database, pathway_index,
                                     pathway_tuples, pathway_to_protein_tuples, GENE_NODETYPE)
            pathway_index += 1

    populate_pathway_table(pathway_tuples, conn)
    populate_pathway_to_protein_table(pathway_to_protein_tuples, conn)
    print('Done.')


def populate_large_static_tables(proteins, peptides, protein_to_peptides, modified_sites, taxcode, protease_id, conn):
    proteins_df = pd.DataFrame(proteins.values())
    proteins_df['PARENT_PROTEIN_ID'] = proteins_df['PARENT_PROTEIN_ID'].astype('Int64')
    proteins_df['TAXCODE'] = taxcode
    proteins_df.to_sql('PROTEIN', conn, if_exists='append', index=False)

    peptides_df = pd.DataFrame(peptides.items(), columns=['SEQUENCE', 'PEPTIDE_ID'])
    peptides_df.to_sql('PEPTIDE', conn, if_exists='append', index=False)

    protein_to_peptides_df = pd.DataFrame(protein_to_peptides)
    protein_to_peptides_df['PROTEASE_ID'] = protease_id
    protein_to_peptides_df.to_sql('PROTEIN_TO_PEPTIDE', conn, if_exists='append', index=False)

    modified_sites_df = pd.DataFrame(modified_sites)
    modified_sites_df.to_sql('MODIFIED_SITE', conn, if_exists='append', index=False)


def insert_proteome_chunk(protein_to_peptides, modified_sites, taxcode, protease_id, conn):
    # proteins_df = pd.DataFrame(proteins.values())
    # proteins_df['PARENT_PROTEIN_ID'] = proteins_df['PARENT_PROTEIN_ID'].astype('Int64')
    # proteins_df['TAXCODE'] = taxcode
    # proteins_df.to_sql('PROTEIN', conn, if_exists='append', index=False)

    protein_to_peptides_df = pd.DataFrame(protein_to_peptides)
    protein_to_peptides_df['PROTEASE_ID'] = protease_id
    protein_to_peptides_df.to_sql('PROTEIN_TO_PEPTIDE', conn, if_exists='append', index=False)

    modified_sites_df = pd.DataFrame(modified_sites)
    modified_sites_df.to_sql('MODIFIED_SITE', conn, if_exists='append', index=False)


def digest_proteome(fasta_path, cleavage_rule_compiled, modification_id, modifiable_residues, peptides,
                    current_protein_id, current_peptide_id, current_modified_site_id,
                    taxcode, protease_id, conn):
    with open(fasta_path) as fasta_parsed:
        proteins = {}
        protein_to_peptides = []
        modified_sites = []
        sequence = ''
        while True:
            line = fasta_parsed.readline().strip()
            if not line or line[0] == '>':
                if sequence:
                    # Digest using Trypsine cleavage rules and up to 4 missed cleavages
                    peptides_of_protein = digest_sequence(sequence, cleavage_rule_compiled, 4)
                    # Get or create peptide ids
                    protein_to_peptides, peptides, current_peptide_id = get_or_create_peptide_ids(
                        peptides_of_protein, peptides, protein_to_peptides,
                        current_peptide_id, current_protein_id)
                    # Extract modified sites
                    modified_sites, current_modified_site_id = extract_modified_sites(
                        modified_sites,
                        current_modified_site_id,
                        sequence,
                        current_protein_id,
                        uniprot,
                        modification_id,
                        modifiable_residues)
                    # Check if the protein is a non-canonical isoform
                    parent_protein_id = get_canonical_protein_id(proteins, rest)
                    # Insert finished protein, maintain as a map with uniprots as keys -
                    # this way isoforms can easily find their parent
                    proteins[uniprot] = {'PROTEIN_ID': current_protein_id, 'UNIPROT_ACC': uniprot,
                                         'GENE_NAME': gene_name, 'PARENT_PROTEIN_ID': parent_protein_id}
                    # Prepare for the next protein
                    if current_protein_id % 10000 == 0:
                        # To avoid memory overflow, insert the protein_to_peptides, and modified_sites dfs already
                        # The proteins and peptides table need to stay
                        print(f'Processed {current_protein_id} proteins')
                        insert_proteome_chunk(protein_to_peptides, modified_sites, taxcode, protease_id, conn)
                        protein_to_peptides = []
                        modified_sites = []
                    current_protein_id += 1
                    sequence = ''
                if line:
                    db, uniprot, rest = line[1:].split('|')
                    gene_name = get_gene_name(rest)
                else:
                    break
            else:
                sequence += line
    return proteins, peptides, protein_to_peptides, modified_sites, \
           current_protein_id, current_peptide_id, current_modified_site_id


def digest_sequence(sequence, cleavage_regex, n_missed_cleavages):
    sequences_wo_missed_cleavages = []
    previous_index = 0
    for match in re.finditer(cleavage_regex, sequence):
        sequences_wo_missed_cleavages.append({
            'seq': sequence[previous_index:match.start() + 1],
            'start': previous_index + 1,
            'end': match.start() + 1
        })
        previous_index = match.start() + 1
    # Add final stretch
    sequences_wo_missed_cleavages.append({
        'seq': sequence[previous_index:],
        'start': previous_index + 1,
        'end': len(sequence)
    })
    sequences_w_missed_cleavages = []
    for i in range(len(sequences_wo_missed_cleavages)):
        for j in range(n_missed_cleavages + 1):
            if i + j < len(sequences_wo_missed_cleavages):
                peptide_seq = "".join([entry['seq'] for entry in sequences_wo_missed_cleavages[i:i + j + 1]])
                sequences_w_missed_cleavages.append({
                    'SEQUENCE': peptide_seq,
                    'START_POSITION': sequences_wo_missed_cleavages[i]['start'],
                    'END_POSITION': sequences_wo_missed_cleavages[i + j]['end']})

    res = []
    for tryptic_peptide in sequences_w_missed_cleavages:
        res.append(tryptic_peptide)
        # Create an additional version where the N-terminal methionine is cleaved away
        if tryptic_peptide['START_POSITION'] == 1 and tryptic_peptide['SEQUENCE'][0] == 'M':
            res.append({'SEQUENCE': tryptic_peptide['SEQUENCE'][1:], 'START_POSITION': 2,
                        'END_POSITION': tryptic_peptide['END_POSITION']})
    return res


def get_or_create_peptide_ids(peptides_of_protein, peptides, protein_to_peptides,
                              current_peptide_id, current_protein_id):
    for peptide in peptides_of_protein:
        if existing_peptide_id := peptides.get(peptide['SEQUENCE']):
            peptide['PEPTIDE_ID'] = existing_peptide_id
        else:
            peptide['PEPTIDE_ID'] = current_peptide_id
            peptides[peptide['SEQUENCE']] = current_peptide_id
            current_peptide_id += 1
        peptide['PROTEIN_ID'] = current_protein_id
        # Remove sequence, it is not stored in the protein_to_peptides table
        peptide.pop('SEQUENCE')
        protein_to_peptides.append(peptide)
    return protein_to_peptides, peptides, current_peptide_id


def get_canonical_protein_id(proteins, rest_string):
    isoform_match = re.search(ISOFORM_REGEX, rest_string)
    if isoform_match:
        parent_protein = proteins.get(isoform_match.group(1))
        if not parent_protein:
            print(f'Canonical Isoform {isoform_match} not found!')
            return None
        else:
            return parent_protein['PROTEIN_ID']
    else:
        return None


def get_gene_name(rest_string):
    gn_match = re.search(GENE_NAME_REGEX, rest_string)
    if gn_match:
        return gn_match.group(1)
    else:
        return None


def extract_modified_sites(modified_sites, current_modified_site_id, protein_sequence, protein_id, uniprot_acc,
                           modification_id, modifiable_residues):
    for index, aa in enumerate(protein_sequence):
        if aa in modifiable_residues:
            modified_sites.append({
                'MODIFIED_SITE_ID': current_modified_site_id,
                'PROTEIN_ID': protein_id,
                'MODIFICATION_ID': modification_id,
                'POSITION': index + 1,
                'RESIDUE': aa,
                'SITE_IDENTIFIER': f'{uniprot_acc}_{aa}{index + 1}'
            })
            current_modified_site_id += 1
    return modified_sites, current_modified_site_id


if __name__ == '__main__':
    print('Initializing the SQLite Backend...')
    db_connection = sqlite3.connect(DB_FILE)
    create_database_schema(db_connection)
    populate_small_static_tables(db_connection)
    process_reference_proteomes(db_connection)
    add_enzyme_substrate_relationships(db_connection)
    import_canonical_pathways(db_connection)
    print('SQLite Backend successfully initialized!')
    db_connection.close()
