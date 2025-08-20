import { saveAs } from 'file-saver'

const utils = {

  downloadSVG: function (svg) {
    const serializer = new XMLSerializer()
    let svgstring = serializer.serializeToString(svg)
    saveAs(new Blob([svgstring], {type: 'image/svg+xml'}), 'download.svg')
  },

  downloadPNG: function (svg) {
    const canvas = document.createElement('canvas')
    canvas.width = svg.width.animVal.value
    canvas.height = svg.height.animVal.value


    const serializer = new XMLSerializer()
    let svgstring = serializer.serializeToString(svg)

    svgstring = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgstring)))

    const canvasContext = canvas.getContext('2d')
    const image = new Image()
    image.src = svgstring
    image.onload = function(){
      canvasContext.drawImage(image, 0, 0)
      saveAs(canvas.toDataURL('image/png'), 'download.png')
    }

  },

  async downloadDxDataGridCSV (fileName, dataGrid, dataFieldFormatters, columnNameFormatters) {
    dataFieldFormatters = dataFieldFormatters || {}
    columnNameFormatters = columnNameFormatters || {}
    const instance = dataGrid.instance

    const data = await instance.getDataSource().store().load()
    const columns = instance.getVisibleColumns().filter(column => column.type !== 'selection')

    const csvHeader = columns.map(column => {
      if (column.dataField in columnNameFormatters) {
        return columnNameFormatters[column.dataField](column)
      }

      if (column.caption in columnNameFormatters) {
        return columnNameFormatters[column.caption](column)
      }

      return column.caption
    })
    const csvData = []

    for (const item of data) {
      csvData.push(columns.map(column => {
        if (column.dataField in dataFieldFormatters) {
          return dataFieldFormatters[column.dataField](item)
        }

        if (column.caption in dataFieldFormatters) {
          return dataFieldFormatters[column.caption](item)
        }

        return column.calculateCellValue(item)
      }))
    }

    this.downloadCSV(fileName, csvData, csvHeader)
  },


  downloadCSV: function (filename, data, header, options) {
    // set default options
    options = Object.assign({
      separator: ',',
      newline: '\n',
      quote: '"'
    }, options)

    const csv = []

    let numCols = data.length > 0 ? data[0].length : 0

    if (header) {
      csv.push(header)
      numCols = header.length
    }

    csv.push(...data)

    // validate
    csv.forEach((row, i) => {
      if (row.length !== numCols) {
        throw new Error(`CSV row ${i} has ${row.length} columns, expected ${numCols} columns`)
      }
    })

    const csvText = csv.map(row => row.map(value => {
          if (value === null || value === undefined) {
            return ''
          }

          value = value.toString()

          if (value.includes(options.quote)) {
            value = value.replace(new RegExp(options.quote, 'g'), options.quote + options.quote)
          }

          if (value.includes(options.separator) || value.includes(options.newline) || value.includes(options.quote)) {
            value = options.quote + value + options.quote
          }

          return value
        }).join(options.separator)
    ).join(options.newline)

    saveAs(
        new Blob([csvText], { type: 'text/csv;charset=utf-8' }),
        filename
    )
  }
}

export default utils
