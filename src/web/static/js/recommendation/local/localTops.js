var calculatedTops = false

var metrics_button = document.getElementById('tops_calc')
var topsTable = document.getElementById('tops-table')
var method_dropdopwn = document.getElementById('method-dropdown')
document.addEventListener('DOMContentLoaded', getPlacesTops())


metrics_button.addEventListener('click', refreshTopTable)
method_dropdopwn.addEventListener('change', () =>
{
    if (method_dropdopwn.value != ""){
        metrics_button.disabled = false
    }
})

function getPlacesTops() {

    method_dropdopwn.selectedIndex = 0
    method_dropdopwn.disabled = true

    if (calculatedTops) {
        return
    }
    metrics_button.disabled = false

    if (method_dropdopwn.value === ""){
        metrics_button.disabled = true
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
        
        
        method_dropdopwn.disabled = false
    })
    
}


function refreshTopTable(){

    while (topsTable.tBodies[0].rows.length > 0){
        topsTable.tBodies[0].deleteRow(0)
    }
    
    let tbody = ""
    
    allMarkers.forEach(mark => {

        tbody += mark.getTableRow(method_dropdopwn.value)
    })

    topsTable.tBodies[0].innerHTML = tbody
}