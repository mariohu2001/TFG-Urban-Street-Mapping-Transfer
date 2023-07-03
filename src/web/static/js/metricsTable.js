var dataTableMetrics = null

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

    dataTableMetrics.rows().remove().draw(false)

    await Promise.all(nodes.map(obtainQualityIndices)).then(
        filas => filas.forEach((fila) =>
            dataTableMetrics.row.add(fila)
        )
    )

    await Promise.all(coordsNodes.map(obtainQualityIndicesCoords)).then(
        filas => filas.forEach( (fila) =>
            dataTableMetrics.row.add(fila)
        )
    )

    dataTableMetrics.draw()
}
