/* ===================================
   API.JS - API wrapper with caching
   =================================== */

const API_BASE = '/api';
const CACHE = new Map();
const CACHE_TTL = {
    sensors: 5 * 60 * 1000,      // 5 minutes
    history: 30 * 60 * 1000,     // 30 minutes
    forecast: 15 * 60 * 1000,    // 15 minutes
    impact: 10 * 60 * 1000,      // 10 minutes
    alerts: 2 * 60 * 1000,       // 2 minutes
};

/**
 * Get cached data or fetch fresh data
 */
function getCached(key) {
    const cached = CACHE.get(key);
    if (cached && cached.expires > Date.now()) {
        return cached.data;
    }
    CACHE.delete(key);
    return null;
}

/**
 * Set cache with TTL
 */
function setCached(key, data, ttl = 5 * 60 * 1000) {
    CACHE.set(key, {
        data,
        expires: Date.now() + ttl,
    });
}

/**
 * Fetch helper with error handling
 */
async function apiFetch(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            timeout: 15000,
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', endpoint, error);
        throw error;
    }
}

/**
 * Get all sensors with current state
 */
export async function getSensors(forceRefresh = false) {
    const cacheKey = 'sensors';
    if (!forceRefresh) {
        const cached = getCached(cacheKey);
        if (cached) return cached;
    }

    const data = await apiFetch('/sensors');
    setCached(cacheKey, data, CACHE_TTL.sensors);
    return data;
}

/**
 * Get sensor by ID
 */
export async function getSensor(sensorId) {
    const sensors = await getSensors();
    return sensors.find(s => s.sensor.id === sensorId);
}

/**
 * Get historical data for a sensor
 */
export async function getSensorHistory(sensorId, hours = 24) {
    const cacheKey = `history_${sensorId}_${hours}`;
    const cached = getCached(cacheKey);
    if (cached) return cached;

    const data = await apiFetch(`/sensors/${sensorId}/history?hours=${hours}`);
    setCached(cacheKey, data, CACHE_TTL.history);
    return data;
}

/**
 * Get traffic environment impact
 */
export async function getImpact(sensorId = null) {
    const cacheKey = `impact_${sensorId || 'all'}`;
    const cached = getCached(cacheKey);
    if (cached) return cached;

    const endpoint = sensorId ? `/impact?sensor_id=${sensorId}` : '/impact';
    const data = await apiFetch(endpoint);
    setCached(cacheKey, data, CACHE_TTL.impact);
    return data;
}

/**
 * Get forecasts (6h, 12h, 24h)
 */
export async function getForecasts(sensorId = null, refresh = false) {
    const cacheKey = `forecast_${sensorId || 'all'}`;
    if (!refresh) {
        const cached = getCached(cacheKey);
        if (cached) return cached;
    }

    const endpoint = sensorId 
        ? `/forecast?sensor_id=${sensorId}&refresh=${refresh}`
        : `/forecast?refresh=${refresh}`;
    const data = await apiFetch(endpoint);
    setCached(cacheKey, data, CACHE_TTL.forecast);
    return data;
}

/**
 * Get active alerts
 */
export async function getAlerts(sensorId = null) {
    const cacheKey = `alerts_${sensorId || 'all'}`;
    const cached = getCached(cacheKey);
    if (cached) return cached;

    const endpoint = sensorId ? `/alerts?sensor_id=${sensorId}` : '/alerts';
    const data = await apiFetch(endpoint);
    setCached(cacheKey, data, CACHE_TTL.alerts);
    return data;
}

/**
 * Get LLM explanation for a sensor
 */
export async function postExplain(sensorId, options = {}) {
    const {
        forceRefreshForecast = false,
        includeHistoryHours = 6,
    } = options;

    const response = await apiFetch('/explain', {
        method: 'POST',
        body: JSON.stringify({
            sensor_id: sensorId,
            force_forecast_refresh: forceRefreshForecast,
            include_history_hours: includeHistoryHours,
        }),
    });

    return response;
}

/**
 * Clear cache
 */
export function clearCache(key = null) {
    if (key) {
        CACHE.delete(key);
    } else {
        CACHE.clear();
    }
}

/**
 * Get cache stats (for debugging)
 */
export function getCacheStats() {
    return {
        size: CACHE.size,
        keys: Array.from(CACHE.keys()),
    };
}
