

const network_visualization = document.getElementById("network_visualization");
const loading_spinner = document.getElementById("loading_spinner")
const degreeRange = document.getElementById("degree-range")
const cityDropDown = document.getElementById("city-select")
const shopCheck = document.getElementById("shopCheck")
const amenityCheck = document.getElementById("amenityCheck")


var nodes = null
var edges = null

var filteredNodes = new vis.DataSet({})

var filteredDegree = null

var visjsNetwork = null

var options = {
    nodes: {
        shape: "dot",
        shapeProperties: {
            interpolation: false
        },
        font: {
            size: 25,
            color: "#000000",
            bold: "true",
            strokeWidth: 5,
            strokeColor: "#ffffff"
        }
    },
    layout: { improvedLayout: false },
    edges: { smooth: false, physics: true },


    physics: {
        barnesHut: {
            avoidOverlap: 0,
            centralGravity: 1,
            damping: 0.09,
            gravitationalConstant: -80000,
            springConstant: 0.001,
            springLength: 300
        },
        enabled: true,
        stabilization: {
            enabled: false,
            fit: true,
            iterations: 1000,
            onlyDynamicEdges: false,
            updateInterval: 50
        }
    }

}

const nodeDegreeFilter = (node) => {
    degreeFilterValue = degreeRange.value

    return parseInt(node.value) >= parseInt(degreeFilterValue)
}

const groupFilter = (node) => {
    let selectedGroups = []

    if (shopCheck.checked) {
        selectedGroups.push(shopCheck.value)
    }

    if (amenityCheck.checked) {
        selectedGroups.push(amenityCheck.value)
    }

    return selectedGroups.includes(node.group)
}




degreeRange.addEventListener("input", function () {
    var filteredDegree = new vis.DataView(filteredNodes, { filter: nodeDegreeFilter })
    filteredDegree.refresh()
    redrawNetwork({ nodes: filteredDegree, edges: edges })
})

shopCheck.addEventListener("change", filterByGroup)
amenityCheck.addEventListener("change", filterByGroup)


cityDropDown.addEventListener("change", cityChanged)

function draw() {

    var data = {
        nodes: nodes,
        edges: edges,
    };

    visjsNetwork = new vis.Network(network_visualization, data, options)
}

function redrawNetwork(data) {

    visjsNetwork.setData(data);
    visjsNetwork.redraw()
}

function filterByGroup()
{
    var filteredGroup = new vis.DataView(nodes, { filter: groupFilter })
    filteredGroup.refresh()
    filteredNodes = filteredGroup
    let degrees = filteredNodes.map(n => n.value)
    var maxDegree = Math.max(...degrees)/2
    degreeRange.max = maxDegree
    degreeRange.value = 0
    redrawNetwork({ nodes: filteredGroup, edges: edges })
}

function cityChanged(e) {
    fetch("/network/" + cityDropDown.value).then(function (response) {
        if (response.ok) {
            return response.json()

        } else {
            console.log("Error en la respuesta")
        }
    }).then(data => {

        nodes = new vis.DataSet(data.nodes)
        edges = new vis.DataSet(data.edges)
        filteredNodes = nodes
        let degrees = nodes.map(n => n.value)
        var maxDegree = Math.max(...degrees)/2
        var degreeFilterValue = maxDegree
        degreeRange.max = maxDegree
        degreeRange.value = 0

        shopCheck.checked = true
        amenityCheck.checked = true

        draw()


    }).catch(function (error) {
        console.log('No se pudo obtener los componentes de la red:' + error.message);
    })
}



// window.addEventListener("load", () => {
//     draw();
// });




// network.on('afterDrawing', function () {
//     loading_spinner.style.display = "none;"
// })

