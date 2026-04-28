/* ===================================
   MAIN.JS - Application entry point
   =================================== */

import { initializeMap, selectSensor } from './map.js';
import { initializeSidebar } from './sidebar.js';
import { initializeCharts, updateChartsForSensor } from './charts.js';
import { initializeViewer3D } from './viewer3d.js';
import { initializeLLMPanel, loadExplanation } from './llm-panel.js';
import { connect, startSimulation, on as wsOn } from './websocket.js';

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
    document.addEventListener('sensor-selected', (event) => {
        const sensorId = event.detail?.sensorId;
        if (sensorId) {
            console.log('📌 Sensor selected:', sensorId);
            updateChartsForSensor(sensorId);
            loadExplanation(sensorId);
        }
    });

    // Global callback for map popup
    window.selectSensorCallback = (sensorId) => {
        selectSensor(sensorId);
        document.dispatchEvent(
            new CustomEvent('sensor-selected', { detail: { sensorId } })
        );
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
