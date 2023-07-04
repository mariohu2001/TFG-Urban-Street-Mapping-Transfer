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

const map = L.map('usmt-map').setView(defaultCoords, 15);

const placesLayer = L.layerGroup().addTo(map);
const coordsLayer = L.layerGroup().addTo(map);

const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 30,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

const nColors = colors.length
var colorIndex = Math.floor(Math.random() * nColors)
var nodeColors = {}
var nodeToId = {}
var nodeCount = 1

nodes.forEach((nodo) => {
    let element = nodo
    nodeToId[element.id] = element
    let lon = element.coords[0];
    let lat = element.coords[1];
    var marker = L.marker([lat, lon], { id: element.id, icon: getMarkerColor(nodeCount), num: nodeCount }).addTo(placesLayer)
    element.num = nodeCount
    element.color = nodeColors[nodeCount]

    let popUpContent = "#" + nodeCount + "</br>" +
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
    nodeCount++
})



coordsNodes.forEach((nodo) => {
    
    var marker = L.marker([nodo.lat, nodo.lon], { icon: getMarkerColor(nodeCount), num: nodeCount }).addTo(coordsLayer)
    nodo.color = nodeColors[nodeCount]
    nodo.num = nodeCount
    let popUpContent = `#${nodeCount}<br>lat: ${nodo.lat.toFixed(7)} lon: ${nodo.lon.toFixed(7)}`
    marker.bindPopup(popUpContent);
    marker.on('mouseover', function (e) {
        this.openPopup();
    });
    marker.on('mouseout', function (e) {
        this.closePopup();
    });
    nodeCount++
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