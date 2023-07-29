
class PlaceMarker {

    constructor(number, color, category, coords, area, id = null, name = null) {
        this.number = number
        this.color = color
        this.category = category
        this.coords = coords
        this.area = area
        this.id = id
        this.name = name
        this.lat = coords[1]
        this.lon = coords[0]
        this.topCats = {}
    }


    createMarker(markerIcon, layer) {
        let marker = L.marker(
            [this.coords[1], this.coords[0]],
            {
                id: this.id,
                icon: markerIcon,
                num: this.number,
            }
        ).addTo(layer)

        let popUpContent = "#" + this.number + "</br>" +
            "<b>" + this.category + "</b>"

        if (this.name !== null) {
            popUpContent += "<br><i>" + this.name + "</i>"
        }

        popUpContent += `<br> lat: ${(this.coords[1]).toFixed(7)} lon: ${(this.coords[0]).toFixed(7)}`
        if (this.id !== null){
            popUpContent += `<br> <b>ID: <i>${this.id}</i></b>`
        }
        marker.bindPopup(popUpContent);
        marker.on('mouseover', function (e) {
            this.openPopup();
        });
        marker.on('mouseout', function (e) {
            this.closePopup();
        });

        this.marker = marker
    }

    assignMarker(marker) {
        this.marker = marker
    }

    assignQualityIndices(qualityIndices) {
        this.qualityIndices = qualityIndices
    }

    assignTopCategories(method, tops) {
        this.topCats[method] = tops
    }

    // getTableRowDataTables(){
    //     return [`<span><i class="bi bi-circle-fill" style="color: ${this.color}; "></i> ` + this.number + '</span>',
    //     nodo.category, datos.Q.toFixed(3), datos.Q_raw.toFixed(3)]
    // }

    getTableRow() {
        icon = `<td><span><i class="bi bi-circle-fill" style="color: ${this.color}; "></i> ${this.number} </span> </td>`
        tops = {}
        tops["Perm"] = this.getTopList("Perm")
        tops["PermRaw"] = this.getTopList("PermRaw")
        tops["Jensen"] = this.getTopList("Jensen")
        tops["JensenRaw"] = this.getTopList("JensenRaw")


        return `<tr> 
        ${icon}
        ${tops["Perm"]}
        ${tops["PermRaw"]}
        ${tops["Jensen"]}
        ${tops["JensenRaw"]}
        </tr>`
    }


    getTopList(method) {
        let methodTops = topCats[method]
        let top = ""
        methodTops.forEach(element => {
            top += `<li> ${element} </li>`
        });
        return `<ol> ${top} </ol>`
    }
}