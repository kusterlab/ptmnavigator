<template>
  <v-app
      id="inspire"
      style="overflow:hidden"
  >
    <PTMNavigator :backend-api="ptmnavigatorplugin" router="router"/>
  </v-app>
</template>

<script>
import PTMNavigator from "@/components/PTMNavigator";
import ptmnavigatorplugin from '../../backend/mock_backend/mockApi'

export default {
  name: 'App',
  components: {
    PTMNavigator,
  },
  data(){
    return{
      ptmnavigatorplugin,
      router:{} //TODO: Implement external router
    }
  }
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
