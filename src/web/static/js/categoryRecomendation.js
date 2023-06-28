


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

const city_dropdown = document.getElementById("city")
const category_dropdown = document.getElementById("category")
const method_dropdown = document.getElementById("metric")
const tabla_metricas = document.getElementById("metrics-table")
const metrics_button = document.getElementById("metrics_button")

var dataTableMetrics = null

$(document).ready(function () {
    dataTableMetrics = $('#metrics-table').DataTable({
        "paging": true, // Desactivar paginado
        "searching": false, // Desactivar búsqueda
        "ordering": true, // Activar ordenación
        "info": false, // Desactivar información de la tabla,
        "pageLength": 5,
        "lengthChange": false
    });
});

const map = L.map('map').setView(defaultCoords, 15);

const marker_layer = L.layerGroup().addTo(map);

metrics_button.addEventListener("click", update_indices_table)

const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 30,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);


var colorIndex = Math.floor(Math.random() * nColors)
var nodeColors = {}
var numToId = {}

city_dropdown.addEventListener("change", change_categories_dropdown)



for (var i = 0; i < nodes.length; i++) {
    let element = nodes[i]
    numToId[element.id] = i
    let lon = element.coords[0];
    let lat = element.coords[1];

    var marker = L.marker([lat, lon], { id: element.id, icon: getMarkerColor() }).addTo(marker_layer)

    let popUpContent = "#" + i  + "</br>" +
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

function getMarkerColor() {
    let marker = L.ExtraMarkers.icon({
        icon: 'fa-circle',
        markerColor: colors[colorIndex % colors.length],
        iconColor: 'white',
        svg: true,
        prefix: 'fas'
    })
    nodeColors[nodes[i].id] = colors[colorIndex % colors.length]
    colorIndex++
    return marker
}



function get_categories_by_city() {
    var city = city_dropdown.value

    network_button.href = "/category_net/" + city

    fetch("/categories/" + city).then(response => {
        if (!response.ok) {
            throw new Error("Error en la respuesta de la petición.");
        }
        return response.json();
    }).then(data => change_categories_dropdown(data))


}

function change_categories_dropdown() {

    fetch("/categories/" + city_dropdown.value).then(response => {
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
}

function obtain_quality_indices(nodo) {
    let url = "/quality_indices/" + method_dropdown.value + "/" + city_dropdown.value + "/" + category_dropdown.value + "/" + nodo.id
    return fetch(url).then(response => {
        if (!response.ok) {
            throw new Error("Error en la respuesta de la petición.");
        }


        return response.json();
    }
    ).catch(function (error) {
        console.error(error);
        throw new Error("Error en la respuesta de la petición.");
    });
}



function update_indices_table() {

    document.getElementById("loading").style.display = "block"

    let indices = nodes.map(function (nodo) { return obtain_quality_indices(nodo) });

    Promise.all(indices)
        .then(function (indice) {
            dataTableMetrics.rows().remove().draw(false)

            indice.forEach(function (ind) {
                let Quality = ind[0]

                let row = [`<span><i class="bi bi-circle-fill" style="color: ${nodeColors[Quality.id]}; "></i> ` + numToId[Quality.id] + '</span>',
                 Quality.category, Quality.Q.toFixed(3), Quality.Q_raw.toFixed(3)]
                dataTableMetrics.row.add(row).draw(false)

            })

            document.getElementById("loading").style.display = "none"
        })
        .catch(function (error) {
            console.error(error);
            throw new Error("Error en la respuesta de la petición.");
        });
}

