/* ===================================
   MAIN.JS - Application entry point
   =================================== */

import { initializeMap, selectSensor } from './map.js?v=20260429b';
import { initializeSidebar } from './sidebar.js?v=20260429b';
import { initializeCharts, updateChartsForSensor } from './charts.js?v=20260429b';
import { initializeViewer3D } from './viewer3d.js?v=20260429b';
import { initializeLLMPanel, loadExplanation } from './llm-panel.js?v=20260429b';
import { connect, startSimulation, on as wsOn } from './websocket.js?v=20260429b';
import { getSensor } from './api.js?v=20260429b';

/**
 * Main application initialization
 */
async function initializeApp() {
    console.log('🚀 UrbanPulse Coruña - Initializing frontend...');

    try {
        // Initialize Leaflet map
        console.log('📍 Initializing Leaflet map...');
        await initializeMap('map');

        // Initialize sidebar
        console.log('📋 Initializing sidebar...');
        await initializeSidebar();

        // Initialize charts
        console.log('📊 Initializing charts...');
        await initializeCharts();

        // Initialize 3D viewer
        console.log('🎥 Initializing 3D viewer...');
        await initializeViewer3D();

        // Initialize LLM panel
        console.log('🤖 Initializing LLM panel...');
        initializeLLMPanel();

        // Setup event handlers
        setupEventHandlers();

        // Try to connect to WebSocket
        console.log('🔌 Connecting to WebSocket...');
        try {
            await connect('http://localhost:5173');
        } catch (error) {
            console.warn('⚠️ WebSocket connection failed, starting simulation mode:', error.message);
            startSimulation(5000); // Simulate data every 5 seconds
        }

        console.log('✅ UrbanPulse Coruña frontend ready!');

    } catch (error) {
        console.error('❌ Initialization error:', error);
        displayErrorPage(error);
    }
}

/**
 * Setup event handlers
 */
function setupEventHandlers() {
    // Sensor selection
    window.addEventListener('sensor-selected', (event) => {
        const sensorId = event.detail?.sensorId;
        if (sensorId) {
            console.log('📌 Sensor selected:', sensorId);
            updateMetricsPanel(sensorId);
            updateChartsForSensor(sensorId);
            loadExplanation(sensorId);
        }
    });

    // Global callback for map popup
    window.selectSensorCallback = (sensorId) => {
        selectSensor(sensorId);
    };

    // WebSocket events
    wsOn('connected', () => {
        console.log('✓ WebSocket connected');
    });

    wsOn('disconnected', (reason) => {
        console.warn('✗ WebSocket disconnected:', reason);
    });

    wsOn('sensor_update', (data) => {
        console.log('📊 Sensor update:', data.sensor_id);
    });

    wsOn('alert_new', (data) => {
        console.warn('⚠️ New alert:', data);
    });

    // Mobile menu toggle
    setupMobileMenu();
}

/**
 * Update the right-hand metrics panel with live sensor data.
 */
async function updateMetricsPanel(sensorId) {
    try {
        const overview = await getSensor(sensorId);
        if (!overview) return;

        const state = overview.state || {};
        const traffic = state.traffic_intensity ?? state.TrafficFlowObserved?.intensity ?? 0;
        const pm25 = state.pm25 ?? state.AirQualityObserved?.pm25 ?? 0;
        const noise = state.noise_laeq ?? state.NoiseLevelObserved?.LAeq ?? 0;
        const no2 = state.no2 ?? state.AirQualityObserved?.no2 ?? 0;

        const selectedSensorName = document.getElementById('selected-sensor-name');
        const metricNo2 = document.getElementById('metric-no2');
        const metricPm25 = document.getElementById('metric-pm25');
        const metricNoise = document.getElementById('metric-noise');
        const metricTraffic = document.getElementById('metric-traffic');

        if (selectedSensorName) selectedSensorName.textContent = overview.sensor?.name || sensorId;
        if (metricNo2) metricNo2.textContent = Number(no2).toFixed(1);
        if (metricPm25) metricPm25.textContent = Number(pm25).toFixed(1);
        if (metricNoise) metricNoise.textContent = Number(noise).toFixed(1);
        if (metricTraffic) metricTraffic.textContent = Number(traffic).toFixed(0);
    } catch (error) {
        console.error('Error updating metrics panel:', error);
    }
}

/**
 * Setup mobile menu
 */
function setupMobileMenu() {
    const menuToggle = document.getElementById('menu-toggle');
    if (!menuToggle) return;

    menuToggle.addEventListener('click', () => {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('open');
    });

    // Close sidebar on outside click (mobile)
    document.addEventListener('click', (e) => {
        const sidebar = document.getElementById('sidebar');
        const menuToggle = document.getElementById('menu-toggle');
        
        if (window.innerWidth < 768 && 
            sidebar.classList.contains('open') &&
            !sidebar.contains(e.target) &&
            !menuToggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });
}

/**
 * Display error page
 */
function displayErrorPage(error) {
    const app = document.getElementById('app');
    if (app) {
        app.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100vh; background: #0a0e27;">
                <div style="text-align: center; max-width: 500px; padding: 40px;">
                    <h1 style="color: #ef4444; margin-bottom: 20px;">❌ Error de inicialización</h1>
                    <p style="color: #cbd5e1; margin-bottom: 20px;">Se produjo un error al cargar la aplicación:</p>
                    <pre style="background: #1a1f3a; border: 1px solid #2d3748; border-radius: 8px; padding: 20px; color: #ff6b6b; overflow-x: auto; text-align: left; font-size: 12px;">
${error.message}
${error.stack || ''}
                    </pre>
                    <button onclick="location.reload()" style="margin-top: 20px; padding: 12px 24px; background: #00d4ff; color: #0a0e27; border: none; border-radius: 6px; cursor: pointer; font-weight: 600;">
                        Reintentar
                    </button>
                </div>
            </div>
        `;
    }
}

/**
 * Application ready check
 */
function bootApp() {
    console.log('📄 DOM ready, starting initialization...');
    initializeApp();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootApp, { once: true });
} else {
    bootApp();
}

// Log to console
console.log('%c🌍 UrbanPulse Coruña', 'font-size: 20px; font-weight: bold; color: #00d4ff;');
console.log('%cResponsive frontend with Leaflet, ChartJS & ThreeJS', 'font-size: 12px; color: #cbd5e1;');
console.log('Version: 1.0.0 | Issue #4');
