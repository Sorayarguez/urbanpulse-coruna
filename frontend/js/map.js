/* ===================================
   MAP.JS - Leaflet map with heatmap
   =================================== */

import { getSensors, getSensorHistory } from './api.js';
import { on as wsOn } from './websocket.js';

// Constants
const CORUNA_CENTER = [43.3713, -8.4194];
const MAP_ZOOM = 13;
const HEATMAP_UPDATE_INTERVAL = 5000;

// Global state
let map = null;
let heatmapLive = null;
let heatmapHistorical = null;
let markers = {};
let heatmapMode = 'realtime'; // 'realtime' or 'historical'
let currentSensorData = {};
let historicalData = {};

/**
 * Initialize Leaflet map
 */
export async function initializeMap(containerId = 'map') {
    const container = await resolveMapContainer(containerId);

    // Create map
    map = L.map(container).setView(CORUNA_CENTER, MAP_ZOOM);

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
        className: 'osm-tiles',
    }).addTo(map);

    // Add layer control
    const layerControl = L.control.layers({}, {}, { position: 'topright' });
    layerControl.addTo(map);

    // Initialize heatmap layers
    heatmapLive = createHeatLayer();
    heatmapHistorical = createHeatLayer();

    // Load sensors
    await loadSensors();

    // Setup event listeners
    setupMapEventListeners();

    return map;
}

function createHeatLayer() {
    if (typeof L.heatLayer === 'function') {
        return L.heatLayer([], {
            max: 150,
            radius: 50,
            blur: 20,
            gradient: {
                0.0: '#00ff00',
                0.25: '#ffff00',
                0.5: '#ff9900',
                0.75: '#ff6600',
                1.0: '#ff0000'
            }
        });
    }

    const fallbackLayer = L.layerGroup();
    fallbackLayer.setLatLngs = () => fallbackLayer;
    return fallbackLayer;
}

async function resolveMapContainer(containerId) {
    const directContainer = typeof containerId === 'string'
        ? document.getElementById(containerId)
        : containerId;

    if (directContainer) {
        return directContainer;
    }

    await new Promise((resolve) => requestAnimationFrame(() => resolve(null)));

    const retryContainer = typeof containerId === 'string'
        ? document.getElementById(containerId)
        : containerId;

    if (retryContainer) {
        return retryContainer;
    }

    throw new Error(`Map container not found: ${containerId}`);
}

/**
 * Load sensors and create markers
 */
async function loadSensors() {
    try {
        const sensorsData = await getSensors();
        
        // Create markers for each sensor
        sensorsData.forEach(sensorState => {
            const sensor = sensorState.sensor;
            const state = sensorState.state;
            const no2 = state.no2 || 0;

            currentSensorData[sensor.id] = state;

            // Create marker with severity color
            const severity = getSeverity(no2);
            const markerIcon = createMarkerIcon(severity);

            const marker = L.marker([sensor.lat, sensor.lon], {
                icon: markerIcon,
                title: sensor.name
            });

            // Create popup content
            const popupContent = createPopupContent(sensor, state);
            marker.bindPopup(popupContent);

            // Click handler
            marker.on('click', () => {
                selectSensor(sensor.id);
            });

            marker.addTo(map);
            markers[sensor.id] = { marker, sensor };
        });

        // Initial heatmap render
        updateHeatmap();

    } catch (error) {
        console.error('Error loading sensors:', error);
    }
}

/**
 * Create custom marker icon
 */
function createMarkerIcon(severity) {
    let color = '#4ade80'; // green (low)
    
    if (severity === 'high') {
        color = '#ef4444'; // red
    } else if (severity === 'medium') {
        color = '#fbbf24'; // orange
    }

    return L.icon({
        iconUrl: `data:image/svg+xml,${encodeURIComponent(`
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32">
                <path d="M12 2C6.48 2 2 6.48 2 12c0 5.52 4.48 10 10 10s10-4.48 10-10S17.52 2 12 2z" fill="${color}"/>
                <circle cx="12" cy="12" r="6" fill="white" opacity="0.3"/>
            </svg>
        `)}`,
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32],
    });
}

/**
 * Determine severity level
 */
function getSeverity(no2) {
    if (no2 > 100) return 'high';
    if (no2 > 60) return 'medium';
    return 'low';
}

/**
 * Create popup content HTML
 */
function createPopupContent(sensor, state) {
    const no2 = (state.no2 || 0).toFixed(1);
    const pm25 = (state.pm25 || 0).toFixed(1);
    const traffic = (state.traffic_intensity || 0).toFixed(0);
    const noise = (state.noise_laeq || 0).toFixed(1);
    const impact = (state.impactScore || 0).toFixed(1);

    return `
        <div class="sensor-popup">
            <h4 style="margin: 0 0 8px 0; color: #00d4ff;">${sensor.name}</h4>
            <div style="font-size: 12px; color: #cbd5e1;">
                <p style="margin: 4px 0;"><strong>NO₂:</strong> ${no2} µg/m³</p>
                <p style="margin: 4px 0;"><strong>PM2.5:</strong> ${pm25} µg/m³</p>
                <p style="margin: 4px 0;"><strong>Tráfico:</strong> ${traffic} veh/h</p>
                <p style="margin: 4px 0;"><strong>Ruido:</strong> ${noise} dB</p>
                <p style="margin: 4px 0;"><strong>Impacto:</strong> ${impact}</p>
            </div>
            <button onclick="window.selectSensorCallback('${sensor.id}')" 
                    style="margin-top: 8px; padding: 4px 8px; background: #00d4ff; color: #0a0e27; border: none; border-radius: 4px; cursor: pointer; font-weight: 500;">
                Ver detalles
            </button>
        </div>
    `;
}

/**
 * Update heatmap with current data
 */
export async function updateHeatmap() {
    try {
        if (!heatmapLive || typeof heatmapLive.setLatLngs !== 'function') {
            return;
        }

        if (heatmapMode === 'realtime') {
            const points = [];
            
            Object.values(markers).forEach(({ sensor }) => {
                const state = currentSensorData[sensor.id];
                if (state && state.no2) {
                    // Normalize NO2 to 0-1 range (assuming max is 150 µg/m³)
                    const intensity = Math.min(state.no2 / 150, 1.0);
                    points.push([sensor.lat, sensor.lon, intensity]);
                }
            });

            heatmapLive.setLatLngs(points);
        } else if (heatmapMode === 'historical') {
            // Load historical data for all sensors
            const points = [];
            
            for (const [sensorId, { sensor }] of Object.entries(markers)) {
                try {
                    if (!historicalData[sensorId]) {
                        const history = await getSensorHistory(sensorId, 24);
                        historicalData[sensorId] = history;
                    }
                    
                    const history = historicalData[sensorId];
                    if (history.AirQualityObserved && history.AirQualityObserved.length > 0) {
                        // Calculate average NO2 for last 24h
                        const avgNo2 = history.AirQualityObserved.reduce((sum, data) => {
                            return sum + (data.no2 || 0);
                        }, 0) / history.AirQualityObserved.length;
                        
                        const intensity = Math.min(avgNo2 / 150, 1.0);
                        points.push([sensor.lat, sensor.lon, intensity]);
                    }
                } catch (error) {
                    console.error(`Error loading historical data for ${sensorId}:`, error);
                }
            }

            heatmapHistorical.setLatLngs(points);
        }
    } catch (error) {
        console.error('Error updating heatmap:', error);
    }
}

/**
 * Set heatmap mode (realtime or historical)
 */
export function setHeatmapMode(mode) {
    if (map) {
        if (heatmapMode === 'realtime' && heatmapLive) {
            map.removeLayer(heatmapLive);
        } else if (heatmapMode === 'historical' && heatmapHistorical) {
            map.removeLayer(heatmapHistorical);
        }

        heatmapMode = mode;

        if (mode === 'realtime' && heatmapLive) {
            map.addLayer(heatmapLive);
        } else if (mode === 'historical' && heatmapHistorical) {
            map.addLayer(heatmapHistorical);
        }

        updateHeatmap();
    }
}

/**
 * Toggle heatmap visibility
 */
export function toggleHeatmap(visible) {
    if (map) {
        const layer = heatmapMode === 'realtime' ? heatmapLive : heatmapHistorical;
        if (visible && !map.hasLayer(layer)) {
            map.addLayer(layer);
        } else if (!visible && map.hasLayer(layer)) {
            map.removeLayer(layer);
        }
    }
}

/**
 * Toggle marker visibility
 */
export function toggleMarkers(visible) {
    if (map) {
        Object.values(markers).forEach(({ marker }) => {
            if (visible && !map.hasLayer(marker)) {
                map.addLayer(marker);
            } else if (!visible && map.hasLayer(marker)) {
                map.removeLayer(marker);
            }
        });
    }
}

/**
 * Update marker for sensor
 */
export function updateMarker(sensorId, state) {
    if (markers[sensorId]) {
        const { marker, sensor } = markers[sensorId];
        currentSensorData[sensorId] = state;

        // Update marker icon color
        const no2 = state.no2 || 0;
        const severity = getSeverity(no2);
        marker.setIcon(createMarkerIcon(severity));

        // Update popup
        const popupContent = createPopupContent(sensor, state);
        marker.setPopupContent(popupContent);
    }
}

/**
 * Select sensor and center map
 */
export function selectSensor(sensorId) {
    if (markers[sensorId]) {
        const { marker } = markers[sensorId];
        map.setView(marker.getLatLng(), 15, { animate: true });
        marker.openPopup();
    }
    
    // Trigger event
    window.dispatchEvent(new CustomEvent('sensor-selected', { detail: { sensorId } }));
}

/**
 * Setup event listeners
 */
function setupMapEventListeners() {
    // Listen to sensor updates via WebSocket
    wsOn('sensor_update', (data) => {
        if (data.sensor_id && data) {
            updateMarker(data.sensor_id, data);
            updateHeatmap();
        }
    });

    // Periodic heatmap updates (for demo/fallback)
    setInterval(updateHeatmap, HEATMAP_UPDATE_INTERVAL);
}

export default {
    initializeMap,
    updateHeatmap,
    setHeatmapMode,
    toggleHeatmap,
    toggleMarkers,
    updateMarker,
    selectSensor,
};
