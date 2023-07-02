


const colors = [

    "#00AA00",
    "#00AAAA",
    "#AA0000",
    "#AA00AA",
    "#FFAA00",
    "#AAAAAA",
    "#5555FF",
    "#55FF55",
    "#55FFFF",
    "#FF5555",
    "#FF55FF",
    "#FFFF55",
    "#FFFFFF",


    "#1abc9c",
    "#a3e4d7",
    "#85c1e9",
    "#2980b9",
    "#af7ac5",
    "#ec7063",
    "#2ecc71",
    "#f4d03f",
    "#f5b041",
    "#dc7633",
    "#abb2b9",
    "red",
    "orange",
    "blue",
    "green",
    "purple",
    "pink",
    "brown",
    "yellow",
    "cyan",
    "magenta",
    "violet",
    "coral",
    "gold",
    "lime",
    "indigo",
    "teal",
    "orchid",
    "salmon",
    "steelblue",
    "tomato"
];

// ['red', 'orange-dark', 'orange', 'yellow', 'blue-dark', 'cyan', 'purple', 'violet', 'pink', 'green-dark', 'green', 'green-light', 'white']
const nColors = colors.length


const category_dropdown = document.getElementById("category")
const method_dropdown = document.getElementById("metric")
const tabla_metricas = document.getElementById("metrics-table")
const metrics_button = document.getElementById("metrics_button")
const transfer_button = document.getElementById("transfer_button")



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
            }
        },
        "pagingType": "simple"
    });
});

const map = L.map('map').setView(defaultCoords, 15);

const places_layer = L.layerGroup().addTo(map);
const coords_layer = L.layerGroup().addTo(map);

transfer_button.addEventListener('click', () => {
    console.log(window.location.search )

    window.location.href = "/transfer" + window.location.search
})

metrics_button.addEventListener("click", update_indices_table)

const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 30,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);


var colorIndex = Math.floor(Math.random() * nColors)
var nodeColors = {}
var nodeToId = {}





for (var i = 0; i < nodes.length; i++) {
    let element = nodes[i]
    nodeToId[element.id] = element
    let lon = element.coords[0];
    let lat = element.coords[1];

    let num = i + 1
    var marker = L.marker([lat, lon], { id: element.id, icon: getMarkerColor(num), num: num, }).addTo(places_layer)
    element.num = num
    element.color = nodeColors[num]

    let popUpContent = "#" + num + "</br>" +
        "<b>" + element.category + "</b>"

    if (element.name !== null && "name" in element) {
        popUpContent += "<br><i>" + element.name + "</i>"
    }

    popUpContent += `<br> lat: ${element.coords[1]} lon: ${element.coords[0]}`
    popUpContent += `<br> <b>ID: <i>${element.id}</i></b>`
    marker.bindPopup(popUpContent);
    marker.on('mouseover', function (e) {
        this.openPopup();
    });
    marker.on('mouseout', function (e) {
        this.closePopup();
    });
}



coordsNodes.forEach((nodo) => {
    let num = i + 1
    nodo.num = num
    var marker = L.marker([nodo.lat, nodo.lon], { icon: getMarkerColor(num), num: num }).addTo(coords_layer)
    nodo.color = nodeColors[num]
    let popUpContent = `#${num}<br>lat: ${nodo.lat.toFixed(7)} lon: ${nodo.lon.toFixed(7)}`
    marker.bindPopup(popUpContent);
    marker.on('mouseover', function (e) {
        this.openPopup();
    });
    marker.on('mouseout', function (e) {
        this.closePopup();
    });
    i++
})


fetch("/categories/" + city).then(response => {
    if (!response.ok) {
        throw new Error("Error en la respuesta de la petición.");
    }
    return response.json();
}).then(categories => {
    while (category_dropdown.options.length > 1) {
        category_dropdown.options.remove(1);
    }
    categories.forEach(element => {
        category_dropdown.innerHTML += "<option value=" + element[0] + ">" + element[1] + "</option>"
    });
})


function getMarkerColor(nodeNum) {
    let marker = L.ExtraMarkers.icon({
        icon: 'fa-circle',
        markerColor: colors[colorIndex % colors.length],
        iconColor: 'white',
        svg: true,
        prefix: 'fas'
    })
    nodeColors[nodeNum] = colors[colorIndex % colors.length]
    colorIndex++
    return marker
}





async function obtain_quality_indices(nodo) {
    let url = "/quality_indices/" + method_dropdown.value + "/" + city + "/" + category_dropdown.value + "/" + nodo.id
    // return fetch(url).then(response => {
    //     if (!response.ok) {
    //         throw new Error("Error en la respuesta de la petición.");
    //     }


    //     return response.json();
    // }
    // ).catch(function (error) {
    //     console.error(error);
    //     throw new Error("Error en la respuesta de la petición.");
    // });

    let respuesta = await fetch(url)
    let datos = await respuesta.json()
    datos = datos[0]
    console.log(datos)
    let row = [`<span><i class="bi bi-circle-fill" style="color: ${nodeColors[nodo.num]}; "></i> ` + nodo.num + '</span>',
    nodo.category, datos.Q.toFixed(3), datos.Q_raw.toFixed(3)]
    return row
}

async function obtain_quality_indices_coords(nodo) {
    let url = "/quality_indices/" + method_dropdown.value + "/" + city + "/" + category_dropdown.value + "/" + nodo.lat + ":" + nodo.lon
    // return fetch(url).then(response => {
    //     if (!response.ok) {
    //         throw new Error("Error en la respuesta de la petición.");
    //     }


    //     return response.json();
    // }
    // ).catch(function (error) {
    //     console.error(error);
    //     throw new Error("Error en la respuesta de la petición.");
    // });

    let respuesta = await fetch(url)
    let datos = await respuesta.json()
    datos = datos[0]
    console.log(datos)
    let row = [`<span><i class="bi bi-circle-fill" style="color: ${nodeColors[nodo.num]}; "></i> ` + nodo.num + '</span>',
    nodo.category, datos.Q.toFixed(3), datos.Q_raw.toFixed(3)]
    return row
}




function update_indices_table() {

    document.getElementById("loading").style.display = "block"
    dataTableMetrics.rows().remove().draw(false)

    Promise.all(nodes.map(obtain_quality_indices)).then(
        filas => filas.forEach((fila) =>
            dataTableMetrics.row.add(fila).draw(false)
        )
    )

    Promise.all(coordsNodes.map(obtain_quality_indices_coords)).then(
        filas => filas.forEach( (fila) =>
            dataTableMetrics.row.add(fila).draw(false)
        )
    )
    document.getElementById("loading").style.display = "none"
    // Promise.all(indices)
    //     .then(function (indice) {
    //         dataTableMetrics.rows().remove().draw(false)

    //         indice.forEach(function (ind) {
    //             console.log(ind)
    //             let Quality = ind[0]
    //             console.log(Quality)
    //             let row = [`<span><i class="bi bi-circle-fill" style="color: ${nodeColors[Quality.id]}; "></i> ` + nodeToId[Quality.id] + '</span>',
    //              Quality.category, Quality.Q.toFixed(3), Quality.Q_raw.toFixed(3)]
    //             dataTableMetrics.row.add(row).draw(false)

    //         })

    //         document.getElementById("loading").style.display = "none"
    //     })
    //     .catch(function (error) {
    //         console.error(error);
    //         throw new Error("Error en la respuesta de la petición.");
    //     });
}

