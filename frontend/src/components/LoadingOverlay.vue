<template>
  <v-overlay
    absolute
    :value="loading"
  >
    <v-layout
      align-center
      justify-center
      column
      fill-height
    >
      <v-flex
        row
        align-center
      >
        <v-progress-circular
          indeterminate
          :size="100"
          :width="10"
          color="white"
        />
      </v-flex>
    </v-layout>
  </v-overlay>
</template>

<script>
export default {
  props: {
    loading: {
      type: Boolean,
      default: false
    }
  }
}
</script>
