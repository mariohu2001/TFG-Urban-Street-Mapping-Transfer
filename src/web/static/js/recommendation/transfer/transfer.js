const cityDropdown = document.getElementById("ciudad")
const metricsButton = document.getElementById("metrics_button")
var method_dropdopwn = document.getElementById('method-dropdown')
var topsTable = document.getElementById('tops-table')
var loading_div = document.getElementById('loading-div')
var calculatedTops = false


window.addEventListener("popstate", ()=> {
    window.location.reload()
})


cityDropdown.addEventListener('change',() => {
    var selectedCity = cityDropdown.value
    
    metrics_button.disabled = false
    method_dropdopwn.selectedIndex = 0
    method_dropdopwn.disabled = true
})

method_dropdopwn.addEventListener('change', ()=>{
    refreshTopTable()
    
})

metricsButton.addEventListener('click', ()=>{
    metricsButton.disabled = true
    method_dropdopwn.disabled = true
    getTransferPlacesTops()

})




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


function getTransferPlacesTops(){
    loading_div.style.display = "block"

    method_dropdopwn.selectedIndex = 0
    method_dropdopwn.disabled = true

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
    
    fetch('/tops/transfer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "target": city,
            "source": cityDropdown.value,
            "places": nodesIds,
            "coords": coords
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
        metricsButton.disabled= false
        loading_div.style.display = "none"
        
    })
    
}





