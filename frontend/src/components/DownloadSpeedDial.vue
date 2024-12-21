<template>
  <v-speed-dial
    v-model="showOptions"
    :top="top"
    :bottom="bottom"
    :right="right"
    :left="left"
    :direction="direction"
    :open-on-hover="openOnHover"
    :transition="transition"
    :absolute="absolute"
  >
    <template #activator>
      <v-btn
        v-model="showOptions"
        :disabled="disabled"
        color="primary"
        fab
        :loading="loading"
      >
        <v-icon v-if="showOptions">
          mdi-close
        </v-icon>
        <v-icon v-else>
          mdi mdi-download
        </v-icon>
      </v-btn>
    </template>
    <v-btn
      v-if="svg"
      :disabled="disabled"
      fab
      small
      @click="raiseEvent('svg')"
    >
      SVG
    </v-btn>
    <v-btn
      v-if="png"
      :disabled="disabled"
      fab
      small
      @click="raiseEvent('png')"
    >
      PNG
    </v-btn>
    <v-btn
      v-if="csv"
      :disabled="disabled"
      fab
      small
      @click="raiseEvent('csv')"
    >
      CSV
    </v-btn>
    <v-btn
      v-if="sif"
      :disabled="disabled"
      fab
      small
      @click="raiseEvent('sif')"
    >
      SIF
    </v-btn>
    <v-btn
      v-if="pdf"
      :disabled="disabled"
      fab
      small
      @click="raiseEvent('pdf')"
    >
      PDF
    </v-btn>
    <v-btn
      v-if="json"
      :disabled="disabled"
      fab
      small
      @click="raiseEvent('json')"
    >
      JSON
    </v-btn>
  </v-speed-dial>
</template>

<script>
export default {
  name: 'DownloadMenu',
  props: {
    absolute: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    top: {
      type: Boolean,
      default: false
    },
    bottom: {
      type: Boolean,
      default: false
    },
    left: {
      type: Boolean,
      default: false
    },
    right: {
      type: Boolean,
      default: false
    },
    png: {
      type: Boolean,
      default: false
    },
    svg: {
      type: Boolean,
      default: false
    },
    csv: {
      type: Boolean,
      default: false
    },
    sif: {
      type: Boolean,
      default: false
    },
    pdf: {
      type: Boolean,
      default: false
    },
    json: {
      type: Boolean,
      default: false
    },
    openOnHover: {
      type: Boolean,
      default: false
    },
    transition: {
      type: String,
      default: 'slide-y-transition'
    },
    direction: {
      type: String,
      default: 'bottom'
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  data: () => ({
    showOptions: false
  }),
  methods: {
    raiseEvent: function (message) {
      this.$emit(message, null)
    }
  }
}
</script>
