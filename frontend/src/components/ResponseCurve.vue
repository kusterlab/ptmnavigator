<template>
  <div>
    <loading-overlay :loading="isLoading" />
    <generic-line-plot
        ref="lineplot"
        id="ic50Plot"
        :curveParameters="responseCurveModel.parameter"
        :dataPoints="responseCurveModel.data"
        :minHeight="minHeight"
        :minWidth="minWidth"
        :title="title"
        :properties="responseCurveModel.properties"
        :x-axis-label="xAxisLabel"
        y-axis-label="Relative Response"
        v-on="$listeners"
        :exponential-x="exponentialX"
        :draw-line="isTimeDependent"
        :legend-at-bottom="legendAtBottom"
        :container-width="containerWidth"
        :scale-svg="scaleSVG"
    />
  </div>
</template>

<script>
//TODO: Remove this once we removed the unreachable code
/* eslint-disable no-unreachable */
import axios from "axios";

import LoadingOverlay from "@/components/LoadingOverlay";
import GenericLinePlot from "@/components/GenericLinePlot";

export default {
  components: {
    GenericLinePlot,
    LoadingOverlay
  },
  props: {
    scaleSVG: {
      type: Number,
      default: null,
    },
    minWidth: {
      type: Number,
      default: 200,
    },
    minHeight: {
      type: Number,
      default: 200,
    },
    containerWidth: {
      type: Number,
      default: null
    },
    title: {
      type: String,
      default: "",
    },
    projectId: {
      type: Number,
      default: -1,
    },
    modelIds: {
      type: Array,
      default: () => [],
    },
    drugNames: {
      type: Array,
      default: () => [],
    },
    dataType: {
      type: String,
      default: "cellSelectivity",
    },
    legendAtBottom: {
      type: Boolean,
      default: false
    },
    isFullProteome: {
      type: Boolean,
      default: false
    },
    isTimeDependent: {
      type: Boolean,
      default: false
    },
    isUserCurve: {
      type: Boolean,
      default: false
    },
    parentPerspective: {
      type: String,
      default: "",
    },
    exponentialX: {
      type: Boolean,
      default: true,
    },
  },
  data: function () {
    return {
      maxCurves: 20,
      responseCurveModel: {},
      defaultCurveModel: {
        data: [],
        parameter: [],
        properties: [
          {
            TREATMENT: " ",
            doseUnit: "Dose",
            responseUnit: "Relative Response",
          },
        ],
      },
      isLoading: false,
      currentAxiosCancelTokenSource: undefined,
    };
  },
  computed: {
    /** @returns {(string | undefined)} */
    sModelIds: function () {
      return this.modelIds && this.modelIds.length <= this.maxCurves
        ? this.modelIds.join(";")
        : undefined;
    },
    /** @returns {(string | undefined)} */
    sDrugNames: function () {
      return this.drugNames && this.drugNames.length <= this.maxCurves
        ? this.drugNames.join(";")
        : undefined;
    },
    /** @returns {string)} */
    xAxisLabel: function() {
      if(this.isTimeDependent){
        const timeUnit = this.responseCurveModel.properties ? this.responseCurveModel.properties[0].timeUnit : ''
        return `Duration [${timeUnit}]`
      }else{
        const doseUnit = this.responseCurveModel.properties ? this.responseCurveModel.properties[0].doseUnit : ''
        return `Dose [${doseUnit}]`
      }
    }
  },
  watch: {
    modelIds: function () {
      this.getData();
    },
  },
  methods: {
    getData: function () {
      let that = this;
      //TODO: Refactor into backend
      console.log('TODO: Reimplement')
      return;
      let urlCurveData =
        this.$store.state.host +
        "/proteomicsdb/logic/" +
        this.dataType +
        "/getCurveData.xsjs";
      if (this.sModelIds) {
        //Create a token so the request can be cancelled if the next one overtakes it
        const cancelTokenSource = axios.CancelToken.source();
        //Abort a possible previous request
        if (this.currentAxiosCancelTokenSource)
          this.currentAxiosCancelTokenSource.cancel();
        this.currentAxiosCancelTokenSource = cancelTokenSource;
        // that.isLoading = true;
        axios
          .get(urlCurveData, {
            params: {
              dr_model_ids: this.sModelIds,
              project_id: this.projectId,
              dr_drug_names: this.sDrugNames,
              isFullProteome: this.isFullProteome,
              isTimeDependent: this.isTimeDependent,
              isUserCurve: this.isUserCurve
            },
            cancelToken: this.currentAxiosCancelTokenSource.token,
          })
          .then(function (response) {
            that.currentAxiosCancelTokenSource = undefined;
            that.responseCurveModel = response.data;
            //GenericLinePlot will plot as text the contents of the "TREATMENT" property.
            //So here we set this property depending on the perspective we're in.
            //In the cellSelectivity view, the property already exists and we don't need to do anything
            //In the others, we print complementary data to provide all necessary information

            const trimString = function(seq, maxSequenceDisplayLength){
              return seq.length > maxSequenceDisplayLength
                  ? `${seq.substr(0, maxSequenceDisplayLength)}...`
                  : seq;
            }

            const formatDuration = function(duration, timeUnit){
              if(duration<1 && timeUnit === "h"){
                return `${(duration*60).toPrecision(2)} min`
              }else{
                return `${duration} ${timeUnit}`
              }
            }

            for (let i = 0; i < that.responseCurveModel.properties.length; i++) {
              let curveProps = that.responseCurveModel.properties[i]
              let curveParams = that.responseCurveModel.parameter[i]
              let legendTitle = trimString(curveProps.sequence || curveProps.gene || curveProps.geneNames || curveProps.uniprotAccs, 25)

              if (that.parentPerspective === 'pathway' && curveProps.gene && curveProps.startPosition) {
                //Replace modified sequence by PTM identifier(s)
                  legendTitle = that.getModifiedResidues(curveProps.sequence, curveProps.startPosition)

                legendTitle += ` @ ${curveProps.gene}`
                if(curveProps.experimentName && curveProps.experimentName !== ''){
                  legendTitle += ` (${curveProps.experimentName})`
                }
              } else {
                legendTitle += " ("
                if (that.parentPerspective === 'protein') {
                  legendTitle += curveProps.drugName || ''
                } else {
                  legendTitle += curveProps.gene || ''
                }
                if(curveProps.experimentName){
                  if(curveProps.drugName || curveProps.gene){
                    legendTitle += ' '
                  }
                  legendTitle += curveProps.experimentName
                }
                legendTitle += ")" + (curveProps.celllineName ? ` @ ${curveProps.celllineName}` : '') +
                    (curveProps.duration && curveProps.timeUnit ? ` (${formatDuration(curveProps.duration, curveProps.timeUnit)})` : '')
              }

              //It's a shame that this is called 'TREATMENT', GenericLinePlot needs refactoring
              //But since several components depend on it it's not trivial
              if (!curveProps.TREATMENT) {
                curveProps.TREATMENT = legendTitle

                curveProps.lineTooltip = "<pre style='text-align: left'>" +
                    `<b>${legendTitle}</b><br><br>` +
                    (curveProps.experimentName ? `Experiment:    ${curveProps.experimentName}<br>` : '') +
                    (curveProps.combination ? `Combination Treatment with ${curveProps.combination}, ` : '') +
                    (curveProps.combinationDoseRatio ? `Ratio: 1:${curveProps.combinationDoseRatio}<br><br>` : '') +
                    ((curveParams["ED50, inflection"] && curveParams["ED50, inflection"].value)
                        ? `EC50:          ${curveParams["ED50, inflection"].value.toExponential(2)} ${ curveParams["ED50, inflection"].std_error ? `± ${curveParams["ED50, inflection"].std_error.toExponential(1)}` : ''} ${curveProps.doseUnit}<br>`
                        : '') +
                    (curveProps.foldChange ? `Fold Change:   ${curveProps.foldChange.toPrecision(3)}<br>` : '') +
                    (curveProps.r2 ? `R2:            ${curveProps.r2.toPrecision(2)}<br>` : '') +
                    "</pre>";

                curveProps.dotTooltipTitle = `<pre style='text-align: left'><b>${legendTitle}</b><br><br>`;
              }
            }
            // this.isLoading = false;
          })
          .catch((error) => {
            if (!axios.isCancel(error)) {
              console.log(error);
            }
          });
      } else {
        this.responseCurveModel = this.defaultCurveModel;
      }
    },
    getSVG: function () {
      return this.$refs.lineplot.getSVG();
    },
      getModifiedResidues (modifiedSequence, startPosition) {
          if (!modifiedSequence) return null
          // Go through the sequence and get the positions of modifications (relative to the peptide)
          let intermediateSequence = modifiedSequence
          const res = []
          let modIndex = intermediateSequence.indexOf('(')
          while (modIndex !== -1) {
              if (modIndex > 0) {
                  const residue = intermediateSequence[modIndex - 1]
                  const absolutePosition = Number(startPosition) + Number(modIndex)
                  res.push(`${residue}${absolutePosition}`)
              }
              intermediateSequence = intermediateSequence.replace(/\([a-z]+\)/, '')
              modIndex = intermediateSequence.indexOf('(')
          }
          return res.join('&')
      },
  },
  created() {
    this.responseCurveModel = this.defaultCurveModel;
    this.$root.$on("abort-pending-request", () => {
      if (this.currentAxiosCancelTokenSource)
        this.currentAxiosCancelTokenSource.cancel();
      this.isLoading = false;
    });

    this.getData();
  },
};
</script>

<style scoped>
.progress {
  margin: 0 auto;
  position: relative;
  left: 33.3%;
  bottom: 50%;
}
</style>
