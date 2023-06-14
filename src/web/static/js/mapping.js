
const map = L.map('map').setView([42.3509202, -3.6889187], 18);

const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 30,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

const marker_layer = L.layerGroup().addTo(map);

const search_btn = document.getElementById("search_btn")

const city_dropdown = document.getElementById("city")
const category_dropdown = document.getElementById("category")
const network_button =document.getElementById("network_button")

search_btn.addEventListener("click", refreshMap)
city_dropdown.addEventListener("change", get_categories_by_city)



function refreshMap() {
    console.log("Cargando nodos en el mapa")

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



    fetch("/places/"+ selected_city + "/" +selected_category)
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

function get_categories_by_city()
{
    var city = city_dropdown.value

    network_button.href = "/category_net/"+city

    fetch("/categories/"+city).then(response => {
        if (!response.ok) {
            throw new Error("Error en la respuesta de la petición.");
        }
        return response.json();}).then(data => change_categories_dropdown(data))


}



function change_categories_dropdown(categories)
{
    while (category_dropdown.options.length > 1)
    {
        category_dropdown.options.remove(1);
    }
    categories.forEach(element => {
        category_dropdown.innerHTML += "<option value="+ element[0] +">"+element[1]+"</option>"
    });
}
