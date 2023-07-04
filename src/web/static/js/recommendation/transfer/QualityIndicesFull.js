async function obtainAllQualityIndices(nodo){
    let url = `/quality_indices/all/${city}/${categoryDropdown.value}/${nodo.id}`
    let respuesta = await fetch(url)
    let datos = await respuesta.json()
    valuesTable.push( {Qjensen: datos.Qjensen, Qjensen_raw: datos.Qjensen_raw, Qpermutation: datos.Qperm, Qpermutation_raw: datos.Qperm_raw})
    let row = [`<span><i class="bi bi-circle-fill" style="color: ${nodeColors[nodo.num]}; "></i> ` + nodo.num + '</span>',
       nodo.category, datos.Qjensen.toFixed(3),datos.Qjensen_raw.toFixed(3) ,datos.Qperm.toFixed(3), datos.Qperm_raw.toFixed(3)]
    return row
}

async function obtainAllQualityIndicesCoords(nodo){
    let url = `/quality_indices/all/${city}/${categoryDropdown.value}/${nodo.lat}:${nodo.lon}`
  
    let respuesta = await fetch(url)
    let datos = await respuesta.json()
    valuesTable.push( {Qjensen: datos.Qjensen, Qjensen_raw: datos.Qjensen_raw, Qpermutation: datos.Qperm, Qpermutation_raw: datos.Qperm_raw})
    let row = [`<span><i class="bi bi-circle-fill" style="color: ${nodeColors[nodo.num]}; "></i> ` + nodo.num + '</span>',
    nodo.category, datos.Qjensen.toFixed(3),datos.Qjensen_raw.toFixed(3) ,datos.Qperm.toFixed(3), datos.Qperm_raw.toFixed(3)]
    return row
}