/* ===================================
   I18N.JS - Internationalization (Spanish/English)
   =================================== */

const translations = {
    es: {
        // Header
        'header.title': 'UrbanPulse',
        'header.search': 'Buscar zonas (ej: Ronda de Outeiro, Cuatro Caminos)',
        
        // Navigation label
        'nav.sidebar': 'Navegación',
        
        // Sidebar - Navigation
        'nav.dashboard': 'Dashboard',
        'nav.traffic': 'Tráfico',
        'nav.air': 'Calidad del Aire',
        'nav.noise': 'Ruido',
        'nav.forecast': 'Predicciones',
        'nav.greenroute': 'GreenRoute',
        'nav.ecozones': 'EcoZones',
        
        // Sidebar - Services
        'sidebar.services': 'Servicios',
        'sidebar.ia': 'Panel IA',
        'sidebar.ia_hint': 'Explicaciones IA',
        'sidebar.ia_desc': 'Selecciona un sensor para obtener explicaciones personalizadas.',
        
        // Metrics
        'metric.no2': 'NO₂',
        'metric.pm25': 'PM2.5',
        'metric.traffic': 'Tráfico',
        'metric.noise': 'Ruido',
        'metric.unit.no2': 'µg/m³',
        'metric.unit.pm25': 'µg/m³',
        'metric.unit.traffic': 'veh/h',
        'metric.unit.noise': 'dB',
        
        // Severity labels
        'severity.good': '✓ Bien',
        'severity.moderate': '⚠ Moderado',
        'severity.warning': '⚠ Malo',
        'severity.critical': '✕ Crítico',
        
        // Buttons
        'button.details': 'Ver detalles',
        'button.back': '← Volver al Dashboard',
        'button.retry': 'Reintentar',
        
        // Page titles
        'page.traffic': '🚗 Vista de Tráfico',
        'page.traffic_desc': 'Análisis de flujos vehiculares en tiempo real',
        'page.air': '💨 Calidad del Aire',
        'page.air_desc': 'Datos de calidad del aire por zona',
        'page.noise': '🔊 Análisis de Ruido',
        'page.noise_desc': 'Niveles de ruido ambiental',
        'page.forecast': '🔮 Predicciones',
        'page.forecast_desc': 'Predicciones de 6, 12 y 24 horas',
        'page.greenroute': '🚴 GreenRoute',
        'page.greenroute_desc': 'Rutas saludables y ecológicas',
        'page.ecozones': '🌱 EcoZones',
        'page.ecozones_desc': 'Gestión de zonas de bajas emisiones',
        
        // Status
        'status.connected': 'Conectado',
        'status.disconnected': 'Desconectado',
        'status.loading': 'Cargando...',
        'status.error': 'Error',
        
        // Messages
        'error.init': 'Error de inicialización',
        'error.loading': 'Error al cargar los datos',
        'error.sensors': 'No se pudieron cargar los sensores',
    },
    en: {
        // Header
        'header.title': 'UrbanPulse',
        'header.search': 'Search zones (e.g: Ronda de Outeiro, Cuatro Caminos)',
        
        // Sidebar - Navigation
        'nav.dashboard': 'Dashboard',
        'nav.traffic': 'Traffic',
        'nav.air': 'Air Quality',
        'nav.noise': 'Noise',
        'nav.forecast': 'Forecasts',
        'nav.greenroute': 'GreenRoute',
        'nav.ecozones': 'EcoZones',
        
        // Sidebar - Services
        'sidebar.services': 'Services',
        'sidebar.ia': 'AI Panel',
        'sidebar.ia_hint': 'AI Explanations',
        'sidebar.ia_desc': 'Select a sensor to get personalized explanations.',
        
        // Metrics
        'metric.no2': 'NO₂',
        'metric.pm25': 'PM2.5',
        'metric.traffic': 'Traffic',
        'metric.noise': 'Noise',
        'metric.unit.no2': 'µg/m³',
        'metric.unit.pm25': 'µg/m³',
        'metric.unit.traffic': 'veh/h',
        'metric.unit.noise': 'dB',
        
        // Severity labels
        'severity.good': '✓ Good',
        'severity.moderate': '⚠ Moderate',
        'severity.warning': '⚠ Poor',
        'severity.critical': '✕ Critical',
        
        // Buttons
        'button.details': 'View details',
        'button.back': '← Back to Dashboard',
        'button.retry': 'Retry',
        
        // Page titles
        'page.traffic': '🚗 Traffic View',
        'page.traffic_desc': 'Real-time vehicle flow analysis',
        'page.air': '💨 Air Quality',
        'page.air_desc': 'Air quality data by zone',
        'page.noise': '🔊 Noise Analysis',
        'page.noise_desc': 'Environmental noise levels',
        'page.forecast': '🔮 Forecasts',
        'page.forecast_desc': '6, 12 and 24 hour forecasts',
        'page.greenroute': '🚴 GreenRoute',
        'page.greenroute_desc': 'Healthy and ecological routes',
        'page.ecozones': '🌱 EcoZones',
        'page.ecozones_desc': 'Low emission zone management',
        
        // Status
        'status.connected': 'Connected',
        'status.disconnected': 'Disconnected',
        'status.loading': 'Loading...',
        'status.error': 'Error',
        
        // Messages
        'error.init': 'Initialization error',
        'error.loading': 'Error loading data',
        'error.sensors': 'Could not load sensors',
    }
};

class I18n {
    constructor() {
        this.currentLang = localStorage.getItem('language') || 'es';
        this.registerLanguageChangeListener();
    }

    t(key) {
        const value = translations[this.currentLang]?.[key];
        
        if (!value) {
            console.warn(`Translation missing: ${key}`);
            return key;
        }
        
        return value;
    }

    setLanguage(lang) {
        if (translations[lang]) {
            this.currentLang = lang;
            localStorage.setItem('language', lang);
            window.dispatchEvent(new CustomEvent('language-changed', { detail: { lang } }));
            return true;
        }
        return false;
    }

    getLanguage() {
        return this.currentLang;
    }

    registerLanguageChangeListener() {
        window.addEventListener('language-changed', () => {
            this.updateUIText();
        });
    }

    updateUIText() {
        // Update all elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            el.textContent = this.t(key);
        });

        // Update placeholders with data-i18n-placeholder attribute
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            el.placeholder = this.t(key);
        });

        // Update titles with data-i18n-title attribute
        document.querySelectorAll('[data-i18n-title]').forEach(el => {
            const key = el.getAttribute('data-i18n-title');
            el.title = this.t(key);
        });
    }
}

export default new I18n();
export { translations };
