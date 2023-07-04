export { loadMapView };



function loadMapView(containerName, coords, zoomlevel) {

    var map = L.map(containerName).setView(coords, zoomlevel)

    var placesLayer = L.layerGroup().addTo(map);
    var coordsLayer = L.layerGroup().addTo(map)

    var tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 30,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    var mapData = {
        map: map,
        placesLayer: placesLayer,
        coordsLayer: coordsLayer,
        tiles: tiles
    }

}