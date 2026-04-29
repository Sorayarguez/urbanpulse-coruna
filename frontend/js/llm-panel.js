/* ===================================
   LLM-PANEL.JS - LLM explanation panel
   =================================== */

import { postExplain } from './api.js?v=20260429b';
import { on as wsOn } from './websocket.js?v=20260429b';

let llmCache = new Map();
let selectedSensorId = null;

/**
 * Initialize LLM panel
 */
export function initializeLLMPanel() {
    // Listen for sensor selection
    window.addEventListener('sensor-selected', (event) => {
        const sensorId = event.detail?.sensorId;
        if (sensorId) {
            loadExplanation(sensorId);
        }
    });

    // Listen for LLM responses via WebSocket
    wsOn('llm_response', (data) => {
        if (data.sensor_id && data.explanation) {
            displayExplanation(data.sensor_id, data.explanation);
        }
    });
}

/**
 * Load and display explanation for sensor
 */
export async function loadExplanation(sensorId) {
    selectedSensorId = sensorId;

    // Check cache
    const cached = llmCache.get(sensorId);
    if (cached && cached.expires > Date.now()) {
        displayExplanation(sensorId, cached.explanation);
        return;
    }

    // Show loading state
    const llmContent = document.getElementById('llm-content');
    if (llmContent) {
        llmContent.innerHTML = '<div class="spinner" style="margin: 20px auto;"></div><p class="text-tertiary text-center">Generando explicación IA...</p>';
    }

    try {
        const response = await postExplain(sensorId, {
            forceRefreshForecast: false,
            includeHistoryHours: 6,
        });

        if (response && response.explanation) {
            // Cache the response
            llmCache.set(sensorId, {
                explanation: response.explanation,
                expires: Date.now() + (2 * 60 * 1000), // 2 minutes
            });

            displayExplanation(sensorId, response.explanation);
        } else {
            displayError('No se pudo generar la explicación');
        }

    } catch (error) {
        console.error('Error loading explanation:', error);
        displayError('Error al obtener la explicación IA');
    }
}

/**
 * Display explanation in panel
 */
function displayExplanation(sensorId, explanation) {
    const llmContent = document.getElementById('llm-content');
    if (!llmContent || selectedSensorId !== sensorId) return;

    const text = explanation.text || 'Sin texto de explicación disponible';
    const source = explanation.source || 'desconocido';

    const sourceLabel = source === 'ollama' 
        ? '🤖 Ollama (Mistral-7B)'
        : '⚙️ Reglas heurísticas';

    llmContent.innerHTML = `
        <div class="llm-response animate-fadeIn">
            <div class="llm-header" style="margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #2d3748;">
                <span class="llm-source" style="font-size: 12px; color: #00d4ff; font-weight: 600;">
                    ${sourceLabel}
                </span>
            </div>
            <div class="llm-text" style="line-height: 1.6; color: #cbd5e1;">
                ${escapeHtml(text)}
            </div>
            <div class="llm-footer" style="margin-top: 16px; padding-top: 12px; border-top: 1px solid #2d3748; display: flex; justify-content: space-between; align-items: center;">
                <span class="llm-time" style="font-size: 12px; color: #94a3b8;">
                    ${new Date().toLocaleTimeString('es-ES')}
                </span>
                <button onclick="window.refreshExplanation()" class="llm-refresh-btn" style="padding: 4px 12px; background: #1a1f3a; border: 1px solid #2d3748; color: #cbd5e1; border-radius: 4px; cursor: pointer; font-size: 12px; transition: all 150ms ease-in-out;">
                    ↻ Actualizar
                </button>
            </div>
        </div>
    `;

    // Attach refresh handler
    window.refreshExplanation = () => {
        loadExplanation(selectedSensorId);
    };
}

/**
 * Display error in panel
 */
function displayError(message) {
    const llmContent = document.getElementById('llm-content');
    if (!llmContent) return;

    llmContent.innerHTML = `
        <div class="llm-error" style="background: rgba(239, 68, 68, 0.1); border-left: 3px solid #ef4444; padding: 12px; border-radius: 4px;">
            <p style="color: #ef4444; font-weight: 600; margin: 0 0 8px 0;">Error</p>
            <p style="color: #cbd5e1; margin: 0; font-size: 14px;">${message}</p>
        </div>
    `;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Clear LLM cache
 */
export function clearLLMCache() {
    llmCache.clear();
}

/**
 * Get selected sensor ID
 */
export function getSelectedSensorId() {
    return selectedSensorId;
}

export default {
    initializeLLMPanel,
    loadExplanation,
    clearLLMCache,
    getSelectedSensorId,
};
