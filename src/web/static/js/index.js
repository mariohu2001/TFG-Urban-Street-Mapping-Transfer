
const map = L.map('map').setView([42.3509202, -3.6889187], 18);

const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 30,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

const marker_layer = L.layerGroup().addTo(map);

const search_btn = document.getElementById("search_btn")

const city_dropdown = document.getElementById("city")
const category_dropdown = document.getElementById("category")

search_btn.addEventListener("click", refreshMap)




function refreshMap() {
    console.log("Cargando nodos en el mapa")

    selected_city = city_dropdown.value
    console.log(selected_city)
    fetch("/coords/" + selected_city)
        .then(response => {
            if (!response.ok) {
                throw new Error("Error en la respuesta de la petición.");
            }
            return response.json();
        })
        .then(data => changeMapCoords(data.lat, data.lon))

        console.log("mitad")


    fetch("/places/"+ selected_city)
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




function renderMarkers(data) {
    marker_layer.clearLayers();
    for (let key in data) {
        let element = data[key]

        let lon = element.coords[0];
        let lat = element.coords[1];
        L.marker([lat, lon]).addTo(marker_layer)
            .bindPopup(element.category);

    };
}






