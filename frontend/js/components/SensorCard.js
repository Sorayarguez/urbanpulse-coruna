/* ===================================
   SENSORCARD.JS - Sensor card component with i18n
   =================================== */

import i18n from '../i18n.js';

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
                    <div class="card-subtitle">${this.sensor.zone_factor ? 'Zone ' + this.sensor.zone_factor.toFixed(1) + 'x' : 'Urban sensor'}</div>
                </div>
                <span class="${statusClass}">${i18n.t('severity.' + severity)}</span>
            </div>

            <div>
                <div class="metric">
                    <span class="metric-label">${i18n.t('metric.no2')}</span>
                    <span class="metric-value">${no2.toFixed(1)}<span class="metric-unit">${i18n.t('metric.unit.no2')}</span></span>
                </div>
                <div class="metric">
                    <span class="metric-label">${i18n.t('metric.pm25')}</span>
                    <span class="metric-value">${pm25.toFixed(1)}<span class="metric-unit">${i18n.t('metric.unit.pm25')}</span></span>
                </div>
                <div class="metric">
                    <span class="metric-label">${i18n.t('metric.traffic')}</span>
                    <span class="metric-value">${Math.round(traffic)}<span class="metric-unit">${i18n.t('metric.unit.traffic')}</span></span>
                </div>
                <div class="metric">
                    <span class="metric-label">${i18n.t('metric.noise')}</span>
                    <span class="metric-value">${noise.toFixed(1)}<span class="metric-unit">${i18n.t('metric.unit.noise')}</span></span>
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
