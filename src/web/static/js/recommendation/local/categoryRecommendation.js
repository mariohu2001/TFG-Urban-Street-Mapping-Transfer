
const categoryDropdown = document.getElementById("category")
const methodDropdown = document.getElementById("metric")
const metricsButton = document.getElementById("metrics_button")
const transferButton = document.getElementById("transfer_button")




transferButton.addEventListener('click', () => {

    window.location.href = "/transfer/"+city + window.location.search
})

metricsButton.addEventListener("click", updateIndicesTable)


fetch("/categories/" + city).then(response => {
    if (!response.ok) {
        throw new Error("Error en la respuesta de la petición.");
    }
    return response.json();
}).then(categories => {
    while (categoryDropdown.options.length > 1) {
        categoryDropdown.options.remove(1);
    }
    categories.forEach(element => {
        categoryDropdown.innerHTML += "<option value=" + element[0] + ">" + element[1] + "</option>"
    });
})

// document.getElementById('tops_button').addEventListener( 'click',
//     () => {
//         // if (calculatedTops) {
//         //     return
//         // }
    
//         let nodesIds = []
//         Object.values(nodesMarkers).forEach((node) => {
//             nodesIds.push({"id":node.id, "number": node.number})
//         })
    
//         let coords = []
//         Object.values(coordsMarkers).forEach((coordM) => {
//             coords.push({ "lat": coordM.lat, "lon": coordM.lon , "number": coordM.number})
//         })
    
//         fetch("/tops", {
//             method: "POST",
//             headers: {
//                 "Content-type": "application/json",
//             },
//             body: JSON.stringify({
//                 "places": nodesIds,
//                 "coords": coords,
//                 "city": city
//             })
//         }).then((response) => response.json())
//         .then((data) => {


//             let places = data.places
//             Object.entries(places).forEach(([k,v]) => {
//                 Object.entries(v).forEach(([method,top]) => {
//                     nodesMarkers[k].assignTopCategories(method, top)
//                 })
//             })
            
//             let coords = data.coords
//             Object.entries(coords).forEach(([k,v]) => {
//                 Object.entries(v).forEach(([method,top]) => {
//                     coordsMarkers[k].assignTopCategories(method, top)
//                 })
//             })
    
    
//         })
    
//     })



