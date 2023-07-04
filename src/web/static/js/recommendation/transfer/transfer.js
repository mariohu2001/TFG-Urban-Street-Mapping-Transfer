const categoryDropdown = document.getElementById("category")
const cityDropdown = document.getElementById("city")
const metricsButton = document.getElementById("metrics_button")




cityDropdown.addEventListener('change',() => {
    var selectedCity = cityDropdown.value

    fetch("/categories/" + city+"/"+selectedCity).then(response => {
        if (!response.ok) {
            throw new Error("Error en la respuesta de la petición.");
        }
        return response.json();
    }).then(data => changeCategoriesDropdown(data))
})


metricsButton.addEventListener('click', async function(){
    await updateIndicesFullTable()
    fetch('/pca', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(valuesTable)
    }).then(
        console.log(JSON.stringify(valuesTable))
    )

})



function changeCategoriesDropdown(categories) {
    while (categoryDropdown.options.length > 1) {
        categoryDropdown.options.remove(1);
    }
    categories.forEach(element => {
        categoryDropdown.innerHTML += "<option value=" + element[0] + ">" + element[1] + "</option>"
    });
}



