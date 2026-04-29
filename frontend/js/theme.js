/* ===================================
   THEME.JS - Dark/Light theme manager
   =================================== */

class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.initTheme();
        this.registerThemeChangeListener();
    }

    initTheme() {
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        this.updateTheme();
    }

    setTheme(theme) {
        if (['light', 'dark'].includes(theme)) {
            this.currentTheme = theme;
            localStorage.setItem('theme', theme);
            document.documentElement.setAttribute('data-theme', theme);
            this.updateTheme();
            window.dispatchEvent(new CustomEvent('theme-changed', { detail: { theme } }));
            return true;
        }
        return false;
    }

    getTheme() {
        return this.currentTheme;
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    updateTheme() {
        const isDark = this.currentTheme === 'dark';
        // Update meta theme-color for mobile
        const metaTheme = document.querySelector('meta[name="theme-color"]');
        if (metaTheme) {
            metaTheme.setAttribute('content', isDark ? '#1a1a1a' : '#f5f1ed');
        }
    }

    registerThemeChangeListener() {
        window.addEventListener('theme-changed', (e) => {
            const isDark = e.detail.theme === 'dark';
            document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        });
    }

    // Detect system preference if available
    detectSystemPreference() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            const systemTheme = localStorage.getItem('theme-system-preference') === 'auto' ? 'dark' : this.currentTheme;
            if (!localStorage.getItem('theme')) {
                this.setTheme(systemTheme);
            }
        }
    }
}

export default new ThemeManager();
