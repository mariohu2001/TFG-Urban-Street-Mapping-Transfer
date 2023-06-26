

const network_visualization = document.getElementById("network_visualization");
const loading_spinner = document.getElementById("loading_spinner")
const degreeRange = document.getElementById("degree-range")

let degrees = nodes.map(n => n.value)
var maxDegree = Math.max(...degrees)
var degreeFilterValue = maxDegree


degreeRange.max = maxDegree

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
            centralGravity: 0.3,
            damping: 0.09,
            gravitationalConstant: -80000,
            springConstant: 0.001,
            springLength: 250
        },
        enabled: true,
        stabilization: {
            enabled: false,
            fit: true,
            iterations: 1000,
            onlyDynamicEdges: false,
            updateInterval: 50
        }
    },
    configure: {
        filter: function (option, path) {
            if (path.indexOf("physics") !== -1) {
              return true;
            }
            if (path.indexOf("smooth") !== -1 || option === "smooth") {
              return true;
            }
            return false;
          },
          container: document.getElementById("physics-config"),
          showButton : false
    }


}



const nodeDegreeFilter = (node) => {
    degreeFilterValue = degreeRange.value

    return parseInt(node.value)  >= parseInt(degreeFilterValue)
}



degreeRange.addEventListener("input", function () {
    var filteredDegree = new vis.DataView(nodes, { filter: nodeDegreeFilter })
    filteredDegree.refresh()
    
    redrawNetwork({ nodes: filteredDegree, edges: edges })
})


function draw() {

    var data = {
        nodes: nodes,
        edges: edges,
    };


    visjsNetwork = new vis.Network(network_visualization, data, options)
}

function redrawNetwork(data) {

    visjsNetwork.setData( data);
    visjsNetwork.redraw()
}

window.addEventListener("load", () => {
    draw();
});




// network.on('afterDrawing', function () {
//     loading_spinner.style.display = "none;"
// })

