var calculatedTops = false



function getPlacesTops() {
    if (calculatedTops) {
        return
    }

    let nodesIds = []
    nodesMarkers.forEach(node => {
        nodesIds.push({"id":node.id, "number": node.number})
    })

    let coords = []
    coordsMarkers.forEach(coordM => {
        coords.push({ "lat": coordM.lat, "lon": coordM.lon , "number": coordsM.number})
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
        data["places"].entries().forEach(([k,v]) => {
            v.entries().forEach(([method,top]) => {
                nodesMarkers[k].assignTopCategories(method, top)
            })
        })

        data["nodes"].entries().forEach(([k,v]) => {
            v.entries().forEach(([method,top]) => {
                coordsMarkers[k].assignTopCategories(method, top)
            })
        })


    })

}