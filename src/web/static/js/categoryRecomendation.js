


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
"#FFFFFF"
    // "#1abc9c",
    // "#a3e4d7",
    // "#85c1e9",
    // "#2980b9",
    // "#af7ac5",
    // "#ec7063",
    // "#2ecc71",
    // "#f4d03f",
    // "#f5b041",
    // "#dc7633",
    // "#abb2b9",
    // "red",
    // "orange",
    // "blue",
    // "green",
    // "purple",
    // "pink",
    // "brown",
    // "yellow",
    // "cyan",
    // "magenta",
    // "violet",
    // "coral",
    // "gold",
    // "lime",
    // "indigo",
    // "teal",
    // "orchid",
    // "salmon",
    // "steelblue",
    // "tomato"
];

// ['red', 'orange-dark', 'orange', 'yellow', 'blue-dark', 'cyan', 'purple', 'violet', 'pink', 'green-dark', 'green', 'green-light', 'white']
const nColors = colors.length

const city_dropdown = document.getElementById("city")
const category_dropdown = document.getElementById("category")
const method_dropdown = document.getElementById("metric")
const tabla = document.getElementById("metrics_table")
const metrics_button = document.getElementById("metrics_button")

const map = L.map('map').setView(defaultCoords, 15);

const marker_layer = L.layerGroup().addTo(map);

metrics_button.addEventListener("click", update_indices_table)

const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 30,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);


var colorIndex = Math.floor(Math.random() * nColors)
var nodeColors = {}


city_dropdown.addEventListener("change", change_categories_dropdown)

for (var i = 0; i < nodes.length; i++) {
    let element = nodes[i]

    let lon = element.coords[0];
    let lat = element.coords[1];

    var marker = L.marker([lat, lon], { id: element.id, icon: getMarkerColor() }).addTo(marker_layer)

    marker.bindPopup(
        "<i>" + element.id + "</i>" + "</br>" +
        "<b>" + element.category.replace("_", " ") + "</b>");
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
    ).catch(function(error) {
        console.error(error);
        throw new Error("Error en la respuesta de la petición.");
      });
}


function update_indices_table() {

    document.getElementById("loading").style.display = "block"

    let indices = nodes.map(function (nodo) { return obtain_quality_indices(nodo) });

    Promise.all(indices)
  .then(function(indice) {
    while (tabla.rows.length > 1) {
        tabla.deleteRow(1);
      }

    indice.forEach(function(ind){
        let Quality = ind[0]

        var row = tabla.insertRow()
        let cell = row.insertCell()
        cell.innerHTML = Quality.id
        cell.style.backgroundColor = nodeColors[Quality.id];
        cell = row.insertCell()
        cell.innerHTML = Quality.category.replace("_", " ")
        cell = row.insertCell()
        cell.innerHTML = Quality.Q.toFixed(3)
        cell = row.insertCell()
        cell.innerHTML = Quality.Q_raw.toFixed(3)
    })
    
    document.getElementById("loading").style.display = "none"
  })
  .catch(function(error) {
    console.error(error);
    throw new Error("Error en la respuesta de la petición.");
  });
}

