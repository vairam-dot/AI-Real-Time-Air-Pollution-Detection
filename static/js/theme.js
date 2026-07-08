// Theme Switcher for Dark/Light Mode
class ThemeSwitcher {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // If no saved theme, use system preference
        if (!localStorage.getItem('theme')) {
            this.theme = this.prefersDark ? 'dark' : 'light';
        }
        
        this.init();
    }

    init() {
        this.applyTheme(this.theme);
        this.setupThemeToggle();
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    setupThemeToggle() {
        const toggleBtn = document.getElementById('themeToggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleTheme());
        }
    }

    toggleTheme() {
        const newTheme = this.theme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    setTheme(theme) {
        this.theme = theme;
        localStorage.setItem('theme', theme);
        this.applyTheme(theme);
    }

    applyTheme(theme) {
        const html = document.documentElement;
        const body = document.body;
        const toggleBtn = document.getElementById('themeToggle');
        const toggleIcon = document.getElementById('themeIcon');
        
        if (theme === 'dark') {
            html.setAttribute('data-theme', 'dark');
            body.classList.add('dark-mode');
            body.classList.remove('light-mode');
            if (toggleIcon) {
                toggleIcon.className = 'fas fa-sun';
                toggleIcon.title = 'Switch to Light Mode';
            }
            if (toggleBtn) {
                toggleBtn.setAttribute('title', 'Switch to Light Mode');
            }
        } else {
            html.setAttribute('data-theme', 'light');
            body.classList.add('light-mode');
            body.classList.remove('dark-mode');
            if (toggleIcon) {
                toggleIcon.className = 'fas fa-moon';
                toggleIcon.title = 'Switch to Dark Mode';
            }
            if (toggleBtn) {
                toggleBtn.setAttribute('title', 'Switch to Dark Mode');
            }
        }
    }
}

// Initialize theme switcher when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.themeSwitcher = new ThemeSwitcher();
    });
} else {
    window.themeSwitcher = new ThemeSwitcher();
}
