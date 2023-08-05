var calculatedTops = false

document.addEventListener('DOMContentLoaded', getPlacesTops())

var tops_button = document.getElementById('tops_calc')
var topsTable = document.getElementById('tops-table')
var method_dropdopwn = document.getElementById('method-dropdown')

tops_button.addEventListener('click', refreshTopTable)

function getPlacesTops() {
    if (calculatedTops) {
        return
    }

    let nodesIds = []
    Object.values(nodesMarkers).forEach(node => {
        nodesIds.push({"id":node.id, "number": node.number})
    })

    let coords = []
    Object.values(coordsMarkers).forEach(coordM => {
        coords.push({ "lat": coordM.lat, "lon": coordM.lon , "number": coordM.number})
    })

    fetch("/tops", {
        method: "POST",
        headers: {
            "Content-type": "application/json",
        },
        body: JSON.stringify({
            "places": nodesIds,
            "coords": coords,
            "city": city
        })
    }).then((response) => response.json())
    .then((data) => {


        Object.entries(data["places"]).forEach(([k,v]) => {

            Object.entries(v).forEach(([method,top]) => {
                nodesMarkers[k].assignTopCategories(method, top)
            })
        })

        Object.entries(data["coords"]).forEach(([k,v]) => {

            Object.entries(v).forEach(([method,top]) => {
                coordsMarkers[k].assignTopCategories(method, top)
            })
        })


    })

}


function refreshTopTable(){

    while (topsTable.tBodies[0].rows.length > 0){
        topsTable.tBodies[0].deleteRow(0)
    }
    
    let tbody = ""
    
    allMarkers.forEach(mark => {
        console.log("a")
        tbody += mark.getTableRow(method_dropdopwn.value)
    })

    topsTable.tBodies[0].innerHTML = tbody
}