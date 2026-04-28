/* ===================================
   CHARTS.JS - ChartJS implementation
   =================================== */

import { getSensorHistory, getForecasts } from './api.js';
import { on as wsOn } from './websocket.js';

let charts = {
    trafficVsNo2: null,
    evolution24h: null,
    indicesRadar: null,
};

/**
 * Initialize all charts
 */
export async function initializeCharts() {
    try {
        // Create chart instances (empty initially)
        createTrafficVsNo2Chart();
        createEvolution24hChart();
        createIndicesRadarChart();

        // Setup event listeners for tab switching
        setupChartTabs();

        // Listen for sensor updates
        wsOn('sensor_update', (data) => {
            // Update charts if sensor is selected
            updateCharts(data);
        });

        wsOn('forecast_update', (data) => {
            // Refresh forecast data
            updateCharts(data);
        });

    } catch (error) {
        console.error('Error initializing charts:', error);
    }
}

/**
 * Create dual-axis chart: Traffic vs NO2
 */
function createTrafficVsNo2Chart() {
    const ctx = document.getElementById('chart-traffic-no2');
    if (!ctx) return;

    charts.trafficVsNo2 = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'NO₂ (µg/m³)',
                    data: [],
                    type: 'line',
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    fill: true,
                    yAxisID: 'y',
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 3,
                    pointBackgroundColor: '#ef4444',
                },
                {
                    label: 'Banda de confianza',
                    data: [],
                    type: 'line',
                    borderColor: 'rgba(239, 68, 68, 0.3)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    fill: true,
                    borderDash: [5, 5],
                    yAxisID: 'y',
                    pointRadius: 0,
                    borderWidth: 1,
                    tension: 0.4,
                },
                {
                    label: 'Tráfico (veh/h)',
                    data: [],
                    type: 'bar',
                    backgroundColor: 'rgba(0, 212, 255, 0.5)',
                    borderColor: '#00d4ff',
                    yAxisID: 'y1',
                    borderRadius: 4,
                },
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#cbd5e1',
                        usePointStyle: true,
                        padding: 15,
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(10, 14, 39, 0.95)',
                    titleColor: '#00d4ff',
                    bodyColor: '#cbd5e1',
                    borderColor: '#2d3748',
                    borderWidth: 1,
                    padding: 10,
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'NO₂ (µg/m³)',
                        color: '#ef4444',
                        font: { size: 12, weight: 'bold' }
                    },
                    ticks: { color: '#cbd5e1' },
                    grid: { color: 'rgba(45, 55, 72, 0.3)' },
                    min: 0,
                    max: 150,
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Tráfico (veh/h)',
                        color: '#00d4ff',
                        font: { size: 12, weight: 'bold' }
                    },
                    ticks: { color: '#cbd5e1' },
                    grid: { drawOnChartArea: false },
                    min: 0,
                    max: 500,
                },
                x: {
                    ticks: { color: '#cbd5e1' },
                    grid: { color: 'rgba(45, 55, 72, 0.3)' },
                }
            }
        }
    });
}

/**
 * Create evolution 24h chart
 */
function createEvolution24hChart() {
    const ctx = document.getElementById('chart-evolution-24h');
    if (!ctx) return;

    charts.evolution24h = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Histórico (24h)',
                    data: [],
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 2,
                    pointBackgroundColor: '#00d4ff',
                },
                {
                    label: 'Predicción +6h',
                    data: [],
                    borderColor: '#fbbf24',
                    backgroundColor: 'rgba(251, 191, 36, 0.1)',
                    borderDash: [5, 5],
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 2,
                    pointBackgroundColor: '#fbbf24',
                },
                {
                    label: 'Predicción +12h',
                    data: [],
                    borderColor: '#ff6b6b',
                    backgroundColor: 'rgba(255, 107, 107, 0.1)',
                    borderDash: [5, 5],
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 2,
                    pointBackgroundColor: '#ff6b6b',
                },
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#cbd5e1',
                        usePointStyle: true,
                        padding: 15,
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(10, 14, 39, 0.95)',
                    titleColor: '#00d4ff',
                    bodyColor: '#cbd5e1',
                    borderColor: '#2d3748',
                    borderWidth: 1,
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'NO₂ (µg/m³)',
                        color: '#00d4ff',
                        font: { size: 12, weight: 'bold' }
                    },
                    ticks: { color: '#cbd5e1' },
                    grid: { color: 'rgba(45, 55, 72, 0.3)' },
                    min: 0,
                    max: 150,
                },
                x: {
                    ticks: { color: '#cbd5e1' },
                    grid: { color: 'rgba(45, 55, 72, 0.3)' },
                }
            }
        }
    });
}

/**
 * Create radar chart for environmental indices
 */
function createIndicesRadarChart() {
    const ctx = document.getElementById('chart-indices-radar');
    if (!ctx) return;

    charts.indicesRadar = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['NO₂', 'PM2.5', 'Ruido', 'Tráfico', 'Impacto'],
            datasets: [
                {
                    label: 'Valores actuales',
                    data: [0, 0, 0, 0, 0],
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0, 212, 255, 0.2)',
                    borderWidth: 2,
                    pointBackgroundColor: '#00d4ff',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#cbd5e1',
                        padding: 15,
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(10, 14, 39, 0.95)',
                    titleColor: '#00d4ff',
                    bodyColor: '#cbd5e1',
                    borderColor: '#2d3748',
                    borderWidth: 1,
                }
            },
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: {
                        color: '#cbd5e1',
                        backdropColor: 'transparent',
                    },
                    grid: {
                        color: 'rgba(45, 55, 72, 0.3)',
                    },
                    pointLabels: {
                        color: '#cbd5e1',
                        font: { size: 11, weight: '600' }
                    }
                }
            }
        }
    });
}

/**
 * Load and display sensor data in charts
 */
export async function updateChartsForSensor(sensorId) {
    try {
        // Load 24h history
        const history = await getSensorHistory(sensorId, 24);
        const forecasts = await getForecasts(sensorId);

        // Extract NO2 data from history
        const airQualityData = history.AirQualityObserved || [];
        const hours = generateHourLabels(24);

        // Prepare traffic and NO2 data
        const trafficData = [];
        const no2Data = [];
        const no2LowData = [];
        const no2HighData = [];

        if (airQualityData.length > 0) {
            // Sample data points across 24 hours
            for (let i = 0; i < 24; i++) {
                const idx = Math.floor((i / 24) * airQualityData.length);
                const dataPoint = airQualityData[idx];
                
                trafficData.push(dataPoint.traffic_intensity || 0);
                no2Data.push(dataPoint.no2 || 0);
                no2LowData.push(Math.max(0, (dataPoint.no2 || 0) - 10));
                no2HighData.push((dataPoint.no2 || 0) + 10);
            }
        }

        // Update dual-axis chart
        if (charts.trafficVsNo2) {
            charts.trafficVsNo2.data.labels = hours;
            charts.trafficVsNo2.data.datasets[0].data = no2Data;
            charts.trafficVsNo2.data.datasets[1].data = no2HighData;
            charts.trafficVsNo2.data.datasets[2].data = trafficData;
            charts.trafficVsNo2.update();
        }

        // Update evolution 24h chart
        if (charts.evolution24h) {
            charts.evolution24h.data.labels = hours;
            charts.evolution24h.data.datasets[0].data = no2Data;
            
            // Add forecast data if available
            if (forecasts && forecasts.length > 0) {
                const forecast6h = forecasts.find(f => f.horizon && f.horizon.value === 6);
                if (forecast6h) {
                    charts.evolution24h.data.datasets[1].data = Array(24).fill(forecast6h.predictedNO2?.value || 0);
                }
                
                const forecast12h = forecasts.find(f => f.horizon && f.horizon.value === 12);
                if (forecast12h) {
                    charts.evolution24h.data.datasets[2].data = Array(24).fill(forecast12h.predictedNO2?.value || 0);
                }
            }
            charts.evolution24h.update();
        }

        // Update radar chart
        if (charts.indicesRadar && airQualityData.length > 0) {
            const latestData = airQualityData[airQualityData.length - 1];
            
            charts.indicesRadar.data.datasets[0].data = [
                Math.min(100, (latestData.no2 || 0) / 1.5),
                Math.min(100, (latestData.pm25 || 0) / 0.5),
                Math.min(100, (latestData.noise_laeq || 50) / 0.7),
                Math.min(100, (latestData.traffic_intensity || 0) / 5),
                latestData.impactScore || 0
            ];
            charts.indicesRadar.update();
        }

    } catch (error) {
        console.error('Error updating charts:', error);
    }
}

/**
 * Generate hour labels for 24h format
 */
function generateHourLabels(hours) {
    const labels = [];
    for (let i = 0; i < hours; i++) {
        labels.push(`${String(i).padStart(2, '0')}:00`);
    }
    return labels;
}

/**
 * Update charts on real-time data
 */
function updateCharts(data) {
    // Update radar chart with latest values
    if (charts.indicesRadar && data) {
        const currentData = charts.indicesRadar.data.datasets[0].data;
        
        if (data.no2) {
            currentData[0] = Math.min(100, data.no2 / 1.5);
        }
        if (data.pm25) {
            currentData[1] = Math.min(100, data.pm25 / 0.5);
        }
        if (data.noise_laeq) {
            currentData[2] = Math.min(100, data.noise_laeq / 0.7);
        }
        if (data.traffic_intensity) {
            currentData[3] = Math.min(100, data.traffic_intensity / 5);
        }
        
        charts.indicesRadar.update('none');
    }
}

/**
 * Setup chart tab switching
 */
function setupChartTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            
            // Update active tab
            tabButtons.forEach(b => b.classList.remove('active'));
            button.classList.add('active');

            // Update content visibility
            tabContents.forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(tabName)?.classList.add('active');

            // Trigger chart resize on tab switch
            setTimeout(() => {
                Object.values(charts).forEach(chart => {
                    if (chart) chart.resize();
                });
            }, 100);
        });
    });
}

export default {
    initializeCharts,
    updateChartsForSensor,
};
