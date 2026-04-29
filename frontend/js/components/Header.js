/* ===================================
   HEADER.JS - Header with search component
   =================================== */

export class Header {
    constructor() {
        this.searchInput = document.getElementById('search-zones');
        this.connectionStatus = document.getElementById('connection-status');
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            window.dispatchEvent(new CustomEvent('search-zones', { detail: { query } }));
        });
    }

    setConnectionStatus(connected) {
        if (this.connectionStatus) {
            this.connectionStatus.style.backgroundColor = connected ? '#4ade80' : '#ef4444';
            this.connectionStatus.title = connected ? 'Conectado' : 'Desconectado';
        }
    }

    setTitle(title) {
        const logo = document.querySelector('.logo');
        if (logo) {
            logo.textContent = title || '🌍 UrbanPulse';
        }
    }
}

export default Header;
