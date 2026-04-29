/* ===================================
   MAPCOMPONENT.JS - Map component with Leaflet
   =================================== */

export class MapComponent {
    constructor() {
        this.map = null;
        this.markers = {};
        this.CORUNA_CENTER = [43.3713, -8.4194];
        this.MAP_ZOOM = 13;
    }

    initialize() {
        const mapContainer = document.getElementById('map');
        if (!mapContainer) {
            console.error('Map container not found');
            return;
        }

        this.map = L.map(mapContainer).setView(this.CORUNA_CENTER, this.MAP_ZOOM);

        // Usar tiles claros y profesionales
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '© CartoDB © OpenStreetMap',
            maxZoom: 19,
            minZoom: 11,
        }).addTo(this.map);

        // Añadir control de capas
        L.control.layers({}, {}, { position: 'topright' }).addTo(this.map);

        return this.map;
    }

    addSensor(sensor, state) {
        const no2 = state.no2 || 0;
        const severity = this.getSeverity(no2);
        const color = this.getColorBySeverity(severity);

        const marker = L.circleMarker([sensor.lat, sensor.lon], {
            radius: 10,
            fillColor: color,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8,
        });

        const popupContent = `
            <div style="font-family: sans-serif; font-size: 12px;">
                <strong style="color: #4a90a4;">${sensor.name}</strong><br>
                NO₂: ${(no2 || 0).toFixed(1)} µg/m³<br>
                Tráfico: ${(state.traffic_intensity || 0).toFixed(0)} veh/h<br>
                <button onclick="window.selectSensor('${sensor.id}')" 
                    style="margin-top: 8px; padding: 6px 12px; background: #4a90a4; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 500;">
                    Ver detalles
                </button>
            </div>
        `;

        marker.bindPopup(popupContent);
        marker.addTo(this.map);

        this.markers[sensor.id] = { marker, sensor, state };

        return marker;
    }

    updateSensorMarker(sensorId, state) {
        if (this.markers[sensorId]) {
            const no2 = state.no2 || 0;
            const severity = this.getSeverity(no2);
            const color = this.getColorBySeverity(severity);
            
            this.markers[sensorId].marker.setStyle({ fillColor: color });
            this.markers[sensorId].state = state;
        }
    }

    centerOn(sensorId) {
        if (this.markers[sensorId]) {
            const { marker } = this.markers[sensorId];
            this.map.setView(marker.getLatLng(), 15, { animate: true });
            marker.openPopup();
        }
    }

    getSeverity(no2) {
        if (no2 > 100) return 'critical';
        if (no2 > 60) return 'warning';
        if (no2 > 40) return 'moderate';
        return 'good';
    }

    getColorBySeverity(severity) {
        const colors = {
            good: '#9eb8a5',       // Verde suave
            moderate: '#d4b896',   // Amarillo/Naranja suave
            warning: '#d4a5a5',    // Rosa suave
            critical: '#a66b6b'    // Rosa más oscuro
        };
        return colors[severity] || colors.good;
    }
}

export default MapComponent;
