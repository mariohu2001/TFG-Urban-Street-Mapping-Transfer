
const map = L.map('map').setView([42.3509202, -3.6889187], 18);

const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 30,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

const marker_layer = L.layerGroup().addTo(map);

const search_btn = document.getElementById("search_btn")

const city_dropdown = document.getElementById("city")
const category_dropdown = document.getElementById("category")
const analysis_button = document.getElementById("analysis_button")

const markerDefaultOpacity = 0.5;

const defaultMarkerSize = [32, 44]
const minMarkerSize = [16, 22]
const zoomBreakPoint = 12

var MarkerSize = defaultMarkerSize


var currentCity = ""
var mapMarkers = []
var selectedPlaces = []
var selectedCoords = []

var selectedIcon = L.ExtraMarkers.icon({
    icon: 'fa-circle',
    markerColor: 'red',
    iconColor: 'white',
    svg: true,
    prefix: 'fas'
})

var coordsIcon = L.ExtraMarkers.icon({
    icon: 'fa-circle',
    markerColor: 'ForestGreen',
    iconColor: 'white',
    svg: true,
    prefix: 'fas'
})


var defaultIcon = L.ExtraMarkers.icon({
    icon: 'fa-circle',
    markerColor: 'cyan',
    iconColor: 'white',
    svg: true,
    prefix: 'fas'
})



analysis_button.addEventListener('click', function () {


    let queryStringPlaces = selectedPlaces.map(function (marker) {
        return 'place=' + encodeURIComponent(marker.options.id)
    }).join('&')

    let queryStringCoords = selectedCoords.map(function (marker) {
        return 'coords=' + encodeURIComponent(marker.getLatLng().lat) + ":" + encodeURIComponent(marker.getLatLng().lng)
    }).join('&')


    window.location.href = "/recomendation?" + queryStringPlaces + "&" +queryStringCoords + "&city=" + city_dropdown.value

});

map.on('click', addCoordsMarker)


function addCoordsMarker(e) {
    newMarker = L.marker(e.latlng, { icon: coordsIcon })


    popUpContent = `<i>lat: ${e.latlng.lat.toFixed(7)} lon: ${e.latlng.lng.toFixed(7)}</i>`
    newMarker.bindPopup(popUpContent);
    newMarker.on('click', function (e) {
        let index = selectedPlaces.indexOf(this);
        selectedCoords.splice(index, 1);
        marker_layer.removeLayer(this)
    })
    newMarker.on('mouseover', function (e) {
        this.openPopup();
    });
    newMarker.on('mouseout', function (e) {
        this.closePopup();
    });

    selectedCoords.push(newMarker)

    newMarker.addTo(marker_layer)
}



search_btn.addEventListener("click", refreshMap)
city_dropdown.addEventListener("change", get_categories_by_city)

map.on("zoom", function () {
    if (map.getZoom() < 12) {
        MarkerSize = minMarkerSize
    }
    else {
        MarkerSize = defaultMarkerSize
    }
})

function refreshMap() {

    // selectedPlaces = []
    var selected_city = city_dropdown.value
    var selected_category = category_dropdown.value

    fetch("/coords/" + selected_city)
        .then(response => {
            if (!response.ok) {
                throw new Error("Error en la respuesta de la petición.");
            }
            return response.json();
        })
        .then(data => changeMapCoords(data.lat, data.lon))



    fetch("/places/" + selected_city + "/" + selected_category)
        .then(response => {
            if (!response.ok) {
                throw new Error("Error en la respuesta de la petición.");
            }
            return response.json();
        })
        .then(data => renderMarkers(data))


}


function changeMapCoords(latitude, longitude) {

    map.flyTo([latitude, longitude], 15)
}



function selectMarker(event) {
    var marker = event.target;


    if (selectedPlaces.includes(marker)) {
        var index = selectedPlaces.indexOf(marker);
        selectedPlaces.splice(index, 1);
        marker.setIcon(defaultIcon)
    } else {

        selectedPlaces.push(marker);
        marker.setIcon(selectedIcon)

    }

}



function cleanUnselectedMarkers() {
    mapMarkers.forEach(marker => {
        if (!selectedPlaces.includes(marker) && !selectedCoords.includes(marker)) {
            marker_layer.removeLayer(marker)
        }
    })
}


function renderMarkers(data) {
    // marker_layer.clearLayers();

    if (currentCity != city_dropdown.value) {
        selectedPlaces = []
        marker_layer.clearLayers();
    }
    currentCity = city_dropdown.value
    cleanUnselectedMarkers()
    for (let key in data) {
        let element = data[key]

        let lon = element.coords[0];
        let lat = element.coords[1];
        var marker = L.marker([lat, lon], { id: element.id, icon: defaultIcon })

        mapMarkers.push(marker)

        marker.addTo(marker_layer)

        let popUpContent = "<b>" + element.category + "</b>"

        if (element.name !== null) {
            popUpContent += "<br><i>" + element.name + "</i>"
        }

        marker.bindPopup(popUpContent);
        marker.on("click", selectMarker)
        marker.on('mouseover', function (e) {
            this.openPopup();
        });
        marker.on('mouseout', function (e) {
            this.closePopup();
        });
    };
}

function get_categories_by_city() {


    var city = city_dropdown.value

    fetch("/categories/" + city).then(response => {
        if (!response.ok) {
            throw new Error("Error en la respuesta de la petición.");
        }
        return response.json();
    }).then(data => change_categories_dropdown(data))


}



function change_categories_dropdown(categories) {
    while (category_dropdown.options.length > 1) {
        category_dropdown.options.remove(1);
    }
    categories.forEach(element => {
        category_dropdown.innerHTML += "<option value=" + element[0] + ">" + element[1] + "</option>"
    });
}
