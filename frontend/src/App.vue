<template>
  <v-app
      id="inspire"
      style="overflow:hidden"
  >
    <component v-if="$route" :is="$route.name" v-bind="$route.props"></component>
  </v-app>
</template>

<script>
import PTMNavigator from "@/components/PTMNavigator";
import StandaloneCustomDataUpload from "@/components/StandaloneCustomDataUpload";
import ptmnavigatorplugin from '../../backend/mock_backend/mockApi'
// import standaloneBackend from '../../backend/standalone_backend/standaloneApi'

export default {
  name: 'App',
  components: {
    PTMNavigator,
    DataUpload: StandaloneCustomDataUpload
  },
  mounted() {
    //Route to the PTMNavigator component
    // this.$router.push({name: 'PTMNavigator', props: {backendApi: standaloneBackend, ptmNavigatorRouter: this.$router}})
    this.$router.push({name: 'PTMNavigator', props: {backendApi: ptmnavigatorplugin, ptmNavigatorRouter: this.$router}})
  },


}
</script>


<style lang="scss">
.v-application--wrap {
  background-color: #eee;
}

/*
 * Global DxDataGrid styles
 */
.dx-state-hover {
  cursor: pointer;
}

.dx-pager .dx-page-sizes .dx-selection, .dx-pager .dx-pages .dx-selection {
  background-color: #b0b0b0;
}
</style>
