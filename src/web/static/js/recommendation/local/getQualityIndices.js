
async function obtainQualityIndicesMethod(nodo) {
    let url = "/quality_indices/" + methodDropdown.value + "/" + city + "/" + categoryDropdown.value + "/" + nodo.id

    let respuesta = await fetch(url)
    let datos = await respuesta.json()
    let row = [`<span><i class="bi bi-circle-fill" style="color: ${nodo.color}; "></i> ` + nodo.number + '</span>',
     nodo.category, datos.Q.toFixed(3),  datos.Q_raw.toFixed(3)]
    return row
}

async function obtainQualityIndicesCoordsMethod(nodo) {
    let url = "/quality_indices/" + methodDropdown.value + "/" + city + "/" + categoryDropdown.value + "/" + nodo.lat + ":" + nodo.lon

    let respuesta = await fetch(url)
    let datos = await respuesta.json()
    let row = [`<span><i class="bi bi-circle-fill" style="color: ${nodo.color}; "></i> ` + nodo.number + '</span>',
       nodo.category, datos.Q.toFixed(3), datos.Q_raw.toFixed(3)]
    return row
}



