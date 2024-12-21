<template>
  <v-card flat>
    <v-card-text class=" d-flex justify-center align-center">
      <v-alert
        color="blue-grey"
        text
        icon="mdi-exclamation"
        class="mt-8 pa-8"
        prominent
      >
        <div style="padding-left: 8px; margin-bottom: 1em">
          This table is not available!<br>
          Did you upload this dataset only just now?<br>
          Then the enrichment analysis is probably still running.<br><br>
          For an input file with 10,000 peptide sequences, <br>
          the kinase activity inference algorithms should run for approx. 1-2 minutes,<br>
          while the pathway enrichment algorithms take approx. 3-5 minutes.<br>
          If you see a red status indicator, something went wrong.<br>
          Please contract a site administrator.<br><br>
          Please note that for non-Phosphoproteomic datasets,<br>only 'PEA Gene-Centric' and 'PEA Gene-Centric Redundant'
          can be performed.<br>
          If you uploaded phospho-sites instead of phospho-peptides,<br>all algorithms can be performed except for K-STAR.
        </div>
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'TheEnrichmentTablePlaceholder'
}
</script>

<style scoped>

</style>
