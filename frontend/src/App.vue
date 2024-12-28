<template>
  <div id="app">
    <PTMNavigator :backend-api="ptmnavigatorplugin"/>
  </div>
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
      ptmnavigatorplugin
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
