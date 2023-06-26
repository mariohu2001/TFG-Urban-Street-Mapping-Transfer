

const network_visualization = document.getElementById("network_visualization");
const loading_spinner = document.getElementById("loading_spinner")

var network = null;

function draw() {

    var data = {
        nodes: nodes,
        edges: edges,
    };

    var options = {
        nodes: {
            shape: "dot",
            shapeProperties: {
                interpolation: false
            },
            font:{
                size: 25,
                color: "#000000",
                bold: "true",
                strokeWidth: 5, 
                strokeColor: "#ffffff"
            }
        },
        layout: { improvedLayout: false },
        edges: { smooth: false, physics: true},
       

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

        }


    }
    network = new vis.Network(network_visualization, data, options)
}

window.addEventListener("load", () => {
    draw();
});


// network.on('afterDrawing', function () {
//     loading_spinner.style.display = "none;"
// })

