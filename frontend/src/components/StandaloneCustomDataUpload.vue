<template>
  <v-container
      class="grey lighten-3 pa-4"
      fluid
  >
    <v-row>
      <v-col cols="12">
        <v-card elevation="0">
          <v-card-title>Data Upload</v-card-title>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'DataUpload',
  metaInfo () {
    return {
      title: 'Upload',
      titleTemplate: '%s',
      meta: [
        { charset: 'utf-8' },
        { name: 'description', content: 'Upload your data to PTMNavigator.' }
      ]
    }
  },
  data: () => ({})
}
</script>

<style scoped>

</style>