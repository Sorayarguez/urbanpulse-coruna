/* ===================================
   SENSORCARD.JS - Sensor card component
   =================================== */

export class SensorCard {
    constructor(sensor, state) {
        this.sensor = sensor;
        this.state = state;
        this.element = null;
    }

    render() {
        const no2 = this.state.no2 || 0;
        const pm25 = this.state.pm25 || 0;
        const traffic = this.state.traffic_intensity || 0;
        const noise = this.state.noise_laeq || 0;

        const severity = this.getSeverity(no2);
        const statusClass = `status-badge ${severity}`;

        this.element = document.createElement('div');
        this.element.className = 'sensor-card';
        this.element.dataset.sensorId = this.sensor.id;

        this.element.innerHTML = `
            <div class="card-header">
                <div>
                    <div class="card-title">${this.sensor.name}</div>
                    <div class="card-subtitle">${this.sensor.zone_factor ? 'Zona ' + this.sensor.zone_factor.toFixed(1) + 'x' : 'Sensor urbano'}</div>
                </div>
                <span class="${statusClass}">${this.getSeverityLabel(severity)}</span>
            </div>

            <div>
                <div class="metric">
                    <span class="metric-label">NO₂</span>
                    <span class="metric-value">${no2.toFixed(1)}<span class="metric-unit">µg/m³</span></span>
                </div>
                <div class="metric">
                    <span class="metric-label">PM2.5</span>
                    <span class="metric-value">${pm25.toFixed(1)}<span class="metric-unit">µg/m³</span></span>
                </div>
                <div class="metric">
                    <span class="metric-label">Tráfico</span>
                    <span class="metric-value">${Math.round(traffic)}<span class="metric-unit">veh/h</span></span>
                </div>
                <div class="metric">
                    <span class="metric-label">Ruido</span>
                    <span class="metric-value">${noise.toFixed(1)}<span class="metric-unit">dB</span></span>
                </div>
            </div>
        `;

        this.element.addEventListener('click', () => {
            window.dispatchEvent(new CustomEvent('sensor-selected', { 
                detail: { sensorId: this.sensor.id } 
            }));
        });

        return this.element;
    }

    getSeverity(no2) {
        if (no2 > 100) return 'critical';
        if (no2 > 60) return 'warning';
        if (no2 > 40) return 'moderate';
        return 'good';
    }

    getSeverityLabel(severity) {
        const labels = {
            good: '✓ Bien',
            moderate: '⚠ Moderado',
            warning: '⚠ Malo',
            critical: '✕ Crítico'
        };
        return labels[severity] || 'Desconocido';
    }

    update(state) {
        this.state = state;
        if (this.element) {
            const newElement = this.render();
            this.element.replaceWith(newElement);
            this.element = newElement;
        }
    }

    setActive(active) {
        if (this.element) {
            if (active) {
                this.element.classList.add('active');
            } else {
                this.element.classList.remove('active');
            }
        }
    }
}

export default SensorCard;
