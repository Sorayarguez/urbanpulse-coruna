/* ===================================
   APP-NEW.JS - Main application entry point (NEW VERSION)
   =================================== */

import Sidebar from './components/Sidebar.js';
import Header from './components/Header.js';
import MapComponent from './components/MapComponent.js';
import SensorCard from './components/SensorCard.js';
import { getSensors, getAlerts } from './api.js';

let currentPage = 'dashboard';
let selectedSensorId = null;
let sensors = [];
let sensorCards = {};
let mapComponent = null;
let header = null;
let sidebar = null;

/**
 * Main initialization
 */
export async function initializeApp() {
    console.log('🚀 UrbanPulse Coruña - Initializing (NEW UI)...');

    try {
        // Initialize components
        header = new Header();
        sidebar = new Sidebar();
        mapComponent = new MapComponent();

        // Initialize map
        mapComponent.initialize();

        // Load sensors
        await loadSensors();

        // Setup event listeners
        setupEventListeners();

        // Update connection status
        header.setConnectionStatus(true);

        console.log('✅ UrbanPulse Coruña ready!');

    } catch (error) {
        console.error('❌ Initialization error:', error);
        displayError(error);
    }
}

/**
 * Load sensors and populate UI
 */
async function loadSensors() {
    try {
        const sensorsData = await getSensors();
        sensors = sensorsData;

        const panel = document.getElementById('sensors-panel');
        panel.innerHTML = '';

        sensorsData.forEach(sensorState => {
            const sensor = sensorState.sensor;
            const state = sensorState.state;

            // Add marker to map
            mapComponent.addSensor(sensor, state);

            // Create sensor card
            const card = new SensorCard(sensor, state);
            const cardElement = card.render();
            panel.appendChild(cardElement);

            sensorCards[sensor.id] = card;
        });

        console.log(`✓ Loaded ${sensorsData.length} sensors`);

    } catch (error) {
        console.error('Error loading sensors:', error);
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Page navigation
    window.addEventListener('page-changed', (e) => {
        currentPage = e.detail.page;
        handlePageChange(currentPage);
    });

    // Sensor selection
    window.addEventListener('sensor-selected', (e) => {
        selectSensor(e.detail.sensorId);
    });

    // Search zones
    window.addEventListener('search-zones', (e) => {
        const query = e.detail.query;
        filterSensorsByZone(query);
    });

    // Global function for popup click handler
    window.selectSensor = selectSensor;
}

/**
 * Handle page changes
 */
function handlePageChange(page) {
    const contentWrapper = document.getElementById('content-wrapper');
    
    switch(page) {
        case 'dashboard':
            // Show normal view
            contentWrapper.style.display = 'grid';
            break;
        case 'traffic':
            showPlaceholder(contentWrapper, '🚗 Vista de Tráfico', 'Análisis de flujos vehiculares en tiempo real');
            break;
        case 'air':
            showPlaceholder(contentWrapper, '💨 Calidad del Aire', 'Datos de calidad del aire por zona');
            break;
        case 'noise':
            showPlaceholder(contentWrapper, '🔊 Análisis de Ruido', 'Niveles de ruido ambiental');
            break;
        case 'forecast':
            showPlaceholder(contentWrapper, '🔮 Predicciones', 'Predicciones de 6, 12 y 24 horas');
            break;
        case 'greenroute':
            showPlaceholder(contentWrapper, '🚴 GreenRoute', 'Rutas saludables y ecológicas');
            break;
        case 'ecozones':
            showPlaceholder(contentWrapper, '🌱 EcoZones', 'Gestión de zonas de bajas emisiones');
            break;
        default:
            contentWrapper.style.display = 'grid';
    }
}

/**
 * Show placeholder for feature pages
 */
function showPlaceholder(container, title, description) {
    container.innerHTML = `
        <div style="grid-column: 1 / -1; display: flex; align-items: center; justify-content: center; min-height: 400px; background: white; border-radius: 12px; box-shadow: 0 2px 12px rgba(45, 90, 112, 0.08);">
            <div style="text-align: center;">
                <h2 style="font-size: 32px; margin-bottom: 16px;">${title}</h2>
                <p style="font-size: 16px; color: #888; margin-bottom: 24px;">${description}</p>
                <button class="btn btn-primary" onclick="document.querySelector('[data-page=\"dashboard\"]').click();">
                    ← Volver al Dashboard
                </button>
            </div>
        </div>
    `;
}

/**
 * Select sensor and update UI
 */
function selectSensor(sensorId) {
    selectedSensorId = sensorId;

    // Update active card
    Object.keys(sensorCards).forEach(id => {
        sensorCards[id].setActive(id === sensorId);
    });

    // Center map on sensor
    mapComponent.centerOn(sensorId);

    console.log('Sensor selected:', sensorId);
}

/**
 * Filter sensors by zone name
 */
function filterSensorsByZone(query) {
    if (!query) {
        // Show all
        Object.values(sensorCards).forEach(card => {
            if (card.element) {
                card.element.style.display = 'block';
            }
        });
        return;
    }

    Object.values(sensorCards).forEach(card => {
        const matches = card.sensor.name.toLowerCase().includes(query) ||
                       (card.sensor.id && card.sensor.id.toLowerCase().includes(query));
        if (card.element) {
            card.element.style.display = matches ? 'block' : 'none';
        }
    });
}

/**
 * Display error message
 */
function displayError(error) {
    const app = document.getElementById('app');
    if (app) {
        app.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100vh; background: #f5f1ed; font-family: sans-serif;">
                <div style="text-align: center; max-width: 500px; padding: 40px;">
                    <h1 style="color: #a66b6b; margin-bottom: 20px;">❌ Error de inicialización</h1>
                    <p style="color: #555; margin-bottom: 20px;">${error.message}</p>
                    <button onclick="location.reload()" class="btn btn-primary">Reintentar</button>
                </div>
            </div>
        `;
    }
}
