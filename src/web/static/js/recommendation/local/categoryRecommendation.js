
const categoryDropdown = document.getElementById("category")
const methodDropdown = document.getElementById("metric")
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





