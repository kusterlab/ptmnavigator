<template>
  <div id="app">
    <PTMNavigator backend-api="TODO"/>
  </div>
</template>

<script>
import PTMNavigator from "@/components/PTMNavigator";

export default {
  name: 'App',
  components: {
    PTMNavigator
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
