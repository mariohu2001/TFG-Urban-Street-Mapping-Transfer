

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
var nodeCount = 1

var allMarkers = []
var nodesMarkers = {}
var coordsMarkers = {}

Object.keys(nodes).forEach((nodeKey) => {

    let nodo = nodes[nodeKey]
    let pMarker = new PlaceMarker(nodeKey, getColor(), nodo.category, nodo.coords,
        nodo.area, nodo.id, nodo.name)
    allMarkers.push(pMarker)
    pMarker.createMarker(getMarkerColor(), placesLayer)
    nodesMarkers[nodeCount] = pMarker
    nodeCount++
})



Object.keys(coordsNodes).forEach((coordsKey) => {

    let coord = coordsNodes[coordsKey]

    let pMarker = new PlaceMarker(coordsKey, getColor(), coord.category, [coord["lon"], coord["lat"]],
        coord.area)
    allMarkers.push(pMarker)
    pMarker.createMarker(getMarkerColor(), coordsLayer)
    coordsMarkers[nodeCount] = pMarker
    nodeCount++
})


function getMarkerColor() {
    let marker = L.ExtraMarkers.icon({
        icon: 'fa-circle',
        markerColor: getColor(),
        iconColor: 'white',
        svg: true,
        prefix: 'fas'
    })
    colorIndex++
    return marker
}

function getColor() {
    return colors[colorIndex % colors.length]
}