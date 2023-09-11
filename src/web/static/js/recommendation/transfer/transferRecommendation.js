
var categories_drop = document.getElementById("categoría")
var method_drop = document.getElementById("method-dropdown")
var table = document.getElementById("tops-table")
var city_drop = document.getElementById("ciudad")
var metrics_btn = document.getElementById("metrics_button")
categories_drop.disabled = true



city_drop.addEventListener("change", getCategoriesByCity)

categories_drop.addEventListener("change", () => {
    metrics_btn.disabled = false
})



metrics_btn.addEventListener('click', getPlacesTops)

function getCategoriesByCity() {

    method_drop.disabled = true
    var city = city_drop.value

    fetch("/categories/" + city).then(response => {
        if (!response.ok) {
            throw new Error("Error en la respuesta de la petición.");
        }
        return response.json();
    }).then(data => changeCategoriesDropdown(data))

    categories_drop.disabled = false
}


function changeCategoriesDropdown(categories) {
    while (categories_drop.options.length > 1) {
        categories_drop.options.remove(1);
    }
    categories.forEach(element => {
        categories_drop.innerHTML += "<option value=" + element[0] + ">" + element[1] + "</option>"
    });
}

function getPlacesTops() {

    method_drop.selectedIndex = 0
    method_drop.disabled = true
    metrics_btn.disabled = true

    document.getElementById("loading-div").style.display = "block"


    let nodesIds = []
    Object.values(nodesMarkers).forEach(node => {
        nodesIds.push({"id":node.id, "number": node.number})
    })
    
    let coords = []
    Object.values(coordsMarkers).forEach(coordM => {
        coords.push({ "lat": coordM.lat, "lon": coordM.lon , "number": coordM.number})
    })
    
    fetch(`/quality_indices/all/${city_drop.value}`, {
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
            nodesMarkers[k].assignQualityIndices(v)

        })
        
        Object.entries(data["coords"]).forEach(([k,v]) => {
            
            coordsMarkers[k].assignQualityIndices(v)

        })
        
        categories_drop.disabled = false
        method_drop.disabled = false
        document.getElementById("loading-div").style.display = "none"

    })
    
}
categories_drop.addEventListener("change", () => {
    method_drop.selectedIndex = 0
})

method_drop.addEventListener("change",get_ranking)

function get_ranking(){
    let sortedMarkers = allMarkers.slice()

    sortedMarkers.sort((a,b) => {
        return b.qualityIndices[categories_drop.value][method_drop.value]  - a.qualityIndices[categories_drop.value][method_drop.value]
    })


    while (table.tBodies[0].rows.length > 0){
        table.tBodies[0].deleteRow(0)
    }
    
    let tbody = ""
    

    for( let i=0; i < sortedMarkers.length; i++){
        let mark = sortedMarkers[i]
        tbody += `<tr class="tops-tr">
        <td>${i+1}º</td>
        <td><span><i class="bi bi-circle-fill" style="color: ${mark.color}; "></i> ${mark.number} </span> </td>
        <td>${mark.category}</td>
        </tr>`
    }
        
    
    table.tBodies[0].innerHTML = tbody
}