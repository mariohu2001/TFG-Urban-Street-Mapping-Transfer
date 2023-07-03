
const categoryDropdown = document.getElementById("category")
const methodDropdown = document.getElementById("metric")
const tablaMetricas = document.getElementById("metrics-table")
const metricsButton = document.getElementById("metrics_button")
const transferButton = document.getElementById("transfer_button")




transferButton.addEventListener('click', () => {
    console.log(window.location.search )

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



async function obtainQualityIndices(nodo) {
    let url = "/quality_indices/" + methodDropdown.value + "/" + city + "/" + categoryDropdown.value + "/" + nodo.id

    let respuesta = await fetch(url)
    let datos = await respuesta.json()
    datos = datos[0]
    let row = [`<span><i class="bi bi-circle-fill" style="color: ${nodeColors[nodo.num]}; "></i> ` + nodo.num + '</span>',
     nodo.category, datos.Q.toFixed(3),  datos.Q_raw.toFixed(3)]
    return row
}

async function obtainQualityIndicesCoords(nodo) {
    let url = "/quality_indices/" + methodDropdown.value + "/" + city + "/" + categoryDropdown.value + "/" + nodo.lat + ":" + nodo.lon

    let respuesta = await fetch(url)
    let datos = await respuesta.json()
    datos = datos[0]
    let row = [`<span><i class="bi bi-circle-fill" style="color: ${nodeColors[nodo.num]}; "></i> ` + nodo.num + '</span>',
       nodo.category, datos.Q.toFixed(3), datos.Q_raw.toFixed(3)]
    return row
}






