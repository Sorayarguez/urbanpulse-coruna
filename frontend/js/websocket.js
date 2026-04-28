/* ===================================
   WEBSOCKET.JS - Real-time data updates
   =================================== */

const RECONNECT_DELAY = 3000;
const MAX_RECONNECT_DELAY = 30000;

let socket = null;
let reconnectAttempts = 0;
let eventListeners = new Map();

/**
 * Connect to WebSocket server
 */
export function connect(url = 'http://localhost:5173') {
    return new Promise((resolve, reject) => {
        try {
            socket = io(url, {
                reconnection: true,
                reconnectionDelay: RECONNECT_DELAY,
                reconnectionDelayMax: MAX_RECONNECT_DELAY,
                reconnectionAttempts: 10,
            });

            socket.on('connect', () => {
                console.log('✓ WebSocket connected');
                reconnectAttempts = 0;
                updateConnectionStatus(true);
                emit('connected');
                resolve(socket);
            });

            socket.on('disconnect', (reason) => {
                console.warn('✗ WebSocket disconnected:', reason);
                updateConnectionStatus(false);
                emit('disconnected', reason);
            });

            socket.on('error', (error) => {
                console.error('WebSocket error:', error);
                emit('error', error);
            });

            socket.on('reconnect_attempt', () => {
                reconnectAttempts++;
                console.log(`Reconnection attempt ${reconnectAttempts}`);
                emit('reconnecting', reconnectAttempts);
            });

            // Sensor data updates
            socket.on('sensor_update', (data) => {
                emit('sensor_update', data);
            });

            // Forecast updates
            socket.on('forecast_update', (data) => {
                emit('forecast_update', data);
            });

            // Alert events
            socket.on('alert_new', (data) => {
                emit('alert_new', data);
            });

            socket.on('alert_resolved', (data) => {
                emit('alert_resolved', data);
            });

            // LLM responses
            socket.on('llm_response', (data) => {
                emit('llm_response', data);
            });

            // Generic message handler
            socket.on('message', (data) => {
                emit('message', data);
            });

        } catch (error) {
            console.error('Connection error:', error);
            reject(error);
        }
    });
}

/**
 * Disconnect WebSocket
 */
export function disconnect() {
    if (socket) {
        socket.disconnect();
        socket = null;
    }
}

/**
 * Check if connected
 */
export function isConnected() {
    return socket && socket.connected;
}

/**
 * Emit event (for testing/simulation)
 */
export function emit(eventName, data) {
    if (eventListeners.has(eventName)) {
        const listeners = eventListeners.get(eventName);
        listeners.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`Error in listener for ${eventName}:`, error);
            }
        });
    }
}

/**
 * Listen to events
 */
export function on(eventName, callback) {
    if (!eventListeners.has(eventName)) {
        eventListeners.set(eventName, []);
    }
    eventListeners.get(eventName).push(callback);

    // Return unsubscribe function
    return () => {
        const listeners = eventListeners.get(eventName);
        const index = listeners.indexOf(callback);
        if (index > -1) {
            listeners.splice(index, 1);
        }
    };
}

/**
 * Listen to event once
 */
export function once(eventName, callback) {
    const unsubscribe = on(eventName, (data) => {
        unsubscribe();
        callback(data);
    });
    return unsubscribe;
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(connected) {
    const indicator = document.getElementById('connection-status');
    if (indicator) {
        if (connected) {
            indicator.classList.remove('offline');
            indicator.title = 'Conectado';
        } else {
            indicator.classList.add('offline');
            indicator.title = 'Desconectado';
        }
    }
}

/**
 * Simulate sensor data for testing (when WebSocket is not available)
 */
export function startSimulation(interval = 5000) {
    console.log('Starting data simulation...');
    
    const sensors = [
        'sensor-001', 'sensor-002', 'sensor-003',
        'sensor-004', 'sensor-005', 'sensor-006'
    ];

    setInterval(() => {
        const sensor = sensors[Math.floor(Math.random() * sensors.length)];
        const data = {
            sensor_id: sensor,
            timestamp: new Date().toISOString(),
            no2: 40 + Math.random() * 80,
            pm25: 20 + Math.random() * 40,
            traffic_intensity: 100 + Math.random() * 400,
            noise_laeq: 55 + Math.random() * 30,
            temperature: 15 + Math.random() * 15,
            humidity: 40 + Math.random() * 50,
            wind_speed: Math.random() * 10,
        };
        emit('sensor_update', data);
    }, interval);
}

export default {
    connect,
    disconnect,
    isConnected,
    emit,
    on,
    once,
    startSimulation,
};
