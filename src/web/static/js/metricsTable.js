var dataTableMetrics = null
var valuesTable = []
$(document).ready(function () {
    dataTableMetrics = $('#metrics-table').DataTable({
        "paging": true,
        "searching": false, 
        "ordering": true, 
        "info": false, 
        "pageLength": 5,
        "lengthChange": false,
        "language": {
            "paginate": {
                "next": `<i class="bi bi-chevron-double-right"></i>`,
                "previous":  `<i class="bi bi-chevron-double-left"></i>`
            },
            "emptyTable": `<div class="spinner-grow text-success" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          `
        },
        "pagingType": "simple",
    });
});


async function updateIndicesTable() {

    valuesTable = []

    dataTableMetrics.rows().remove().draw(false)

    await Promise.all(nodes.map(obtainQualityIndicesMethod)).then(
        filas => filas.forEach((fila) =>
            dataTableMetrics.row.add(fila)
        )
    )

    await Promise.all(coordsNodes.map(obtainQualityIndicesCoordsMethod)).then(
        filas => filas.forEach( (fila) =>
            dataTableMetrics.row.add(fila)
        )
    )

    dataTableMetrics.draw()
}


async function updateIndicesFullTable() {
    valuesTable = []

    dataTableMetrics.rows().remove().draw(false)

    await Promise.all(nodes.map(obtainAllQualityIndices)).then(
        filas => filas.forEach((fila) =>
            dataTableMetrics.row.add(fila)
        )
    )

    await Promise.all(coordsNodes.map(obtainAllQualityIndicesCoords)).then(
        filas => filas.forEach( (fila) =>
            dataTableMetrics.row.add(fila)
        )
    )
    dataTableMetrics.draw()
}

