const map = L.map('map').setView([48.3794, 31.1656], 6);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
}).addTo(map);

function createFieldPopup(field) {
    const editButton = userPermissions.canChangeField 
        ? `<a href="${field.editUrl}" 
              class="btn btn-sm btn-outline-success w-100">
                Змінити
           </a>` 
        : '';

    console.log(userPermissions.canChangeField)

    const deleteButton = userPermissions.canDeleteField 
        ? `<a href="${field.deleteUrl}" 
              class="btn btn-sm btn-outline-danger w-100">
               Видалити
           </a>` 
        : '';

    const footerHtml = (editButton || deleteButton)
        ? `
            <hr class="map-popup-divider">
            <div class="d-flex justify-content-between gap-2 mt-2">
                ${editButton}
                ${deleteButton}
            </div>
          `
        : '';

    return `
        <div class="map-popup-container">
            <h5 class="map-popup-title">
                🌾 ${field.name}
            </h5>

            <hr class="map-popup-divider">

            <div class="mb-2">
                <b>Площа:</b> 
                ${field.area} га<br>

                <b>Статус:</b> 
                <span class="badge bg-secondary">
                    ${field.status}
                </span>
            </div>
            
            ${footerHtml}
        </div>
    `;
}

function renderFieldsOnMap(fieldsData) {
    const boundsGroup = L.featureGroup();

    fieldsData.forEach(field => {
        if (!field.geom) return;

        const polygon = L.geoJSON(field.geom, {
            coordsToLatLng: function (coords) {
                return new L.LatLng(coords[1], coords[0]);
            },
            style: {
                color: "#198754",
                weight: 3,
                opacity: 0.8,
                fillColor: "#198754",
                fillOpacity: 0.3
            }
        })
        .bindPopup(createFieldPopup(field))
        .addTo(map);

        polygon.on('mouseover', function () {
            this.setStyle({ 
                fillOpacity: 0.5, 
                weight: 4, 
                color: "#0f5132" 
            });
        });

        polygon.on('mouseout', function () {
            this.setStyle({ 
                fillOpacity: 0.3, 
                weight: 3,
                color: "#198754" 
            });
        });

        boundsGroup.addLayer(polygon);
    });

    if (boundsGroup.getLayers().length > 0) {
        map.fitBounds(
            boundsGroup.getBounds(), 
            { padding: [40, 40] }
        );
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const rawData = document.getElementById('fields-data').textContent;
    try {
        const fields = JSON.parse(rawData || '[]');
        renderFieldsOnMap(fields);
    } catch (e) {
        console.error("Помилка парсингу JSON з полями:", e);
    }
});