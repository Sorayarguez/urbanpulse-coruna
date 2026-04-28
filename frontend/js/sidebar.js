/* ===================================
   SIDEBAR.JS - Sensor list and controls
   =================================== */

import { getSensors, getAlerts } from './api.js';
import { on as wsOn } from './websocket.js';
import { selectSensor, setHeatmapMode, toggleHeatmap, toggleMarkers } from './map.js';

let selectedSensorId = null;

/**
 * Initialize sidebar
 */
export async function initializeSidebar() {
    try {
        // Load sensors
        await loadSensorList();

        // Load alerts
        await loadAlerts();

        // Setup event listeners
        setupSidebarEventListeners();

    } catch (error) {
        console.error('Error initializing sidebar:', error);
    }
}

/**
 * Load and render sensor list
 */
async function loadSensorList() {
    try {
        const sensorsData = await getSensors();
        const sensorList = document.getElementById('sensor-list');
        
        if (!sensorList) return;

        sensorList.innerHTML = '';

        sensorsData.forEach(sensorState => {
            const sensor = sensorState.sensor;
            const state = sensorState.state;
            const no2 = (state.no2 || 0).toFixed(1);
            const impact = (state.impactScore || 0).toFixed(0);

            const listItem = document.createElement('li');
            listItem.className = 'sensor-item';
            listItem.dataset.sensorId = sensor.id;

            const content = document.createElement('div');
            content.style.flex = '1';

            const nameEl = document.createElement('div');
            nameEl.className = 'sensor-name';
            nameEl.textContent = sensor.name;
            content.appendChild(nameEl);

            const metricsEl = document.createElement('div');
            metricsEl.className = 'sensor-no2';
            metricsEl.innerHTML = `
                <div>NO₂: <strong>${no2}</strong> µg/m³</div>
            `;
            content.appendChild(metricsEl);

            const impactEl = document.createElement('div');
            impactEl.className = 'sensor-impact';
            impactEl.textContent = `Impacto: ${impact}`;
            content.appendChild(impactEl);

            listItem.appendChild(content);

            // Click handler
            listItem.addEventListener('click', () => {
                selectSensorFromList(sensor.id, listItem);
            });

            sensorList.appendChild(listItem);
        });

    } catch (error) {
        console.error('Error loading sensor list:', error);
    }
}

/**
 * Load and render alerts
 */
async function loadAlerts() {
    try {
        const alerts = await getAlerts();
        const alertsContainer = document.getElementById('alerts-container');
        
        if (!alertsContainer) return;

        if (!alerts || alerts.length === 0) {
            alertsContainer.innerHTML = '<p class="text-tertiary text-center p-md">Sin alertas activas</p>';
            return;
        }

        alertsContainer.innerHTML = '';

        alerts.forEach(alert => {
            const alertEl = document.createElement('div');
            alertEl.className = `alert-item severity-${alert.severity}`;

            alertEl.innerHTML = `
                <div class="alert-severity">${alert.severity.toUpperCase()}</div>
                <div class="alert-message">${alert.message}</div>
                <div class="alert-time">${new Date(alert.timestamp).toLocaleTimeString('es-ES')}</div>
            `;

            alertsContainer.appendChild(alertEl);
        });

    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

/**
 * Select sensor from list
 */
function selectSensorFromList(sensorId, listItem) {
    // Update selected state
    document.querySelectorAll('.sensor-item').forEach(item => {
        item.classList.remove('active');
    });
    listItem.classList.add('active');

    selectedSensorId = sensorId;

    // Center map and trigger event
    selectSensor(sensorId);
}

/**
 * Setup event listeners
 */
function setupSidebarEventListeners() {
    // Layer toggles
    const toggleHeatmapCheckbox = document.getElementById('toggle-heatmap');
    if (toggleHeatmapCheckbox) {
        toggleHeatmapCheckbox.addEventListener('change', (e) => {
            toggleHeatmap(e.target.checked);
        });
    }

    const toggleMarkersCheckbox = document.getElementById('toggle-markers');
    if (toggleMarkersCheckbox) {
        toggleMarkersCheckbox.addEventListener('change', (e) => {
            toggleMarkers(e.target.checked);
        });
    }

    // Heatmap mode
    const heatmapModeRadios = document.querySelectorAll('input[name="heatmap-mode"]');
    heatmapModeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.checked) {
                setHeatmapMode(e.target.value);
            }
        });
    });

    // Listen to sensor updates for list updates
    wsOn('sensor_update', (data) => {
        if (data.sensor_id) {
            updateSensorListItem(data.sensor_id, data);
        }
    });

    // Listen to new alerts
    wsOn('alert_new', (data) => {
        addAlertToList(data);
    });

    // Listen to resolved alerts
    wsOn('alert_resolved', (data) => {
        removeAlertFromList(data.id);
    });

    // Menu toggle (mobile)
    const menuToggle = document.getElementById('menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('open');
        });
    }

    // Mobile: Close sidebar when sensor is selected
    document.addEventListener('sensor-selected', () => {
        const sidebar = document.getElementById('sidebar');
        if (window.innerWidth < 768) {
            sidebar.classList.remove('open');
        }
    });
}

/**
 * Update sensor list item with new data
 */
function updateSensorListItem(sensorId, state) {
    const listItem = document.querySelector(`[data-sensor-id="${sensorId}"]`);
    if (!listItem) return;

    const no2 = (state.no2 || 0).toFixed(1);
    const impact = (state.impactScore || 0).toFixed(0);

    const metricsEl = listItem.querySelector('.sensor-no2');
    if (metricsEl) {
        metricsEl.innerHTML = `
            <div>NO₂: <strong>${no2}</strong> µg/m³</div>
        `;
    }

    const impactEl = listItem.querySelector('.sensor-impact');
    if (impactEl) {
        impactEl.textContent = `Impacto: ${impact}`;
    }
}

/**
 * Add alert to list
 */
function addAlertToList(alert) {
    const alertsContainer = document.getElementById('alerts-container');
    if (!alertsContainer) return;

    // Clear "no alerts" message
    if (alertsContainer.querySelector('.text-tertiary')) {
        alertsContainer.innerHTML = '';
    }

    const alertEl = document.createElement('div');
    alertEl.className = `alert-item severity-${alert.severity}`;
    alertEl.dataset.alertId = alert.id;
    alertEl.innerHTML = `
        <div class="alert-severity">${alert.severity.toUpperCase()}</div>
        <div class="alert-message">${alert.message}</div>
        <div class="alert-time">${new Date().toLocaleTimeString('es-ES')}</div>
    `;

    alertsContainer.insertBefore(alertEl, alertsContainer.firstChild);

    // Limit to 10 alerts
    while (alertsContainer.children.length > 10) {
        alertsContainer.removeChild(alertsContainer.lastChild);
    }
}

/**
 * Remove alert from list
 */
function removeAlertFromList(alertId) {
    const alertEl = document.querySelector(`[data-alert-id="${alertId}"]`);
    if (alertEl) {
        alertEl.style.animation = 'fadeOut 300ms ease-in-out forwards';
        setTimeout(() => {
            alertEl.remove();
        }, 300);
    }
}

/**
 * Get selected sensor ID
 */
export function getSelectedSensorId() {
    return selectedSensorId;
}

export default {
    initializeSidebar,
    getSelectedSensorId,
};
