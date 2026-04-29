/* ===================================
   SIDEBAR.JS - Sidebar navigation component
   =================================== */

export class Sidebar {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.navItems = document.querySelectorAll('.nav-item');
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                this.setActive(item);
                const page = item.dataset.page;
                window.dispatchEvent(new CustomEvent('page-changed', { detail: { page } }));
            });
        });
    }

    setActive(item) {
        this.navItems.forEach(i => i.classList.remove('active'));
        item.classList.add('active');
    }

    updateLLMContent(text) {
        const llmPanel = document.getElementById('llm-content-sidebar');
        if (llmPanel) {
            llmPanel.textContent = text;
        }
    }
}

export default Sidebar;
