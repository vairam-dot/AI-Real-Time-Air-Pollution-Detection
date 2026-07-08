// Interactive Features for AirPollutionAI
class InteractiveDashboard {
    constructor() {
        this.charts = {};
        this.alerts = [];
        this.favorites = this.loadFavorites();

        this.init();
    }

    init() {
        this.setupKeyboardShortcuts();
        this.setupNotifications();
    }

    // Keyboard shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'r') { e.preventDefault(); this.refreshData(); }
            if (e.ctrlKey && e.key === 'f') { e.preventDefault(); document.getElementById('planRoute')?.click(); }
            if (e.ctrlKey && e.key === 's') { e.preventDefault(); document.getElementById('shareBtn')?.click(); }
            if (e.key === 'Escape') this.clearAlerts();
        });
    }

    // Browser notifications
    setupNotifications() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }

    sendNotification(title, body) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, { body, icon: '/static/icon.png' });
        }
    }

    // Favorites
    loadFavorites() { const s = localStorage.getItem('favorites'); return s ? JSON.parse(s) : []; }
    addFavorite(name, location) { this.favorites.push({ name, location, timestamp: Date.now() }); localStorage.setItem('favorites', JSON.stringify(this.favorites)); this.updateFavoritesUI(); }
    removeFavorite(i) { this.favorites.splice(i,1); localStorage.setItem('favorites', JSON.stringify(this.favorites)); this.updateFavoritesUI(); }

    // Data export
    exportData(format = 'csv') {
        const data = { aqiHistory: window.aqiHistory || [], alerts: this.alerts, timestamp: new Date().toISOString() };
        if (format === 'csv') { let csv = 'Time,AQI\n'; data.aqiHistory.forEach(h => csv += `${h.time},${h.value}\n`); this.downloadFile(csv, 'aqi-data.csv', 'text/csv'); }
        else { this.downloadFile(JSON.stringify(data, null, 2), 'aqi-data.json', 'application/json'); }
    }

    downloadFile(content, filename, type) { const blob = new Blob([content], { type }); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = filename; a.click(); URL.revokeObjectURL(url); }

    // Refresh data
    refreshData() { if (typeof socket !== 'undefined') socket.emit('request_update', window.currentLocation || { lat: 28.6139, lon: 77.2090 }); }

    showWeather() { document.getElementById('weather')?.scrollIntoView({ behavior: 'smooth' }); }
    showAlerts() { document.getElementById('alertBar')?.scrollIntoView({ behavior: 'smooth' }); }
    clearAlerts() { const el = document.getElementById('alertBar'); if (!el) return; el.style.opacity='0.5'; setTimeout(()=>el.style.opacity='1',1000); }

    updateFavoritesUI() { const c = document.getElementById('favorites-list'); if (!c) return; c.innerHTML = this.favorites.map((fav,i)=>`<div class="favorite-item"><span>📍 ${fav.name}</span><button onclick="dashboard.removeFavorite(${i})">✖</button></div>`).join(''); }
}

// Initialize (do not overwrite existing dashboard created by inline page scripts)
if (!window.dashboard) {
    window.dashboard = new InteractiveDashboard();
}

// Try to trigger the page's location initialization after all inline scripts run.
// Use load event (addEventListener) so we don't overwrite any window.onload assignments.
window.addEventListener('load', () => {
    // If the page provides getCurrentLocation/initMaps and socket, call them to ensure live location is set.
    try {
        if (typeof getCurrentLocation === 'function') {
            getCurrentLocation().then(location => {
                if (location && typeof socket !== 'undefined') {
                    try { socket.emit('request_update', { lat: location.lat, lon: location.lon }); } catch(e){}
                    if (typeof initMaps === 'function') initMaps(location.lat, location.lon);
                }
            }).catch(() => {});
        }
    } catch (e) {
        console.warn('Error triggering location initialization:', e);
    }
    // Replace the Refresh Location button to prefer a direct high-accuracy geolocation retry.
    try {
        const refreshBtn = document.getElementById('refreshLocation');
        if (refreshBtn) {
            // Remove existing listeners by replacing the node
            const newBtn = refreshBtn.cloneNode(true);
            refreshBtn.parentNode.replaceChild(newBtn, refreshBtn);
            newBtn.addEventListener('click', async () => {
                if (!navigator.geolocation) {
                    document.getElementById('locationName').innerHTML = '📍 Geolocation not supported in your browser';
                    return;
                }
                document.getElementById('locationName').innerHTML = '📍 Requesting precise location...';
                navigator.geolocation.getCurrentPosition(async pos => {
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    document.getElementById('locationName').innerHTML = `📍 ${lat.toFixed(4)}, ${lon.toFixed(4)} (precise)`;
                    try { if (typeof socket !== 'undefined') socket.emit('request_update', { lat, lon }); } catch(e){}
                    try { if (typeof initMaps === 'function') initMaps(lat, lon); } catch(e){}
                }, async err => {
                    console.warn('High-accuracy location failed', err);
                    // fallback to original getCurrentLocation which may use IP fallback
                    if (typeof getCurrentLocation === 'function') {
                        const loc = await getCurrentLocation();
                        try { if (typeof socket !== 'undefined') socket.emit('request_update', { lat: loc.lat, lon: loc.lon }); } catch(e){}
                        try { if (typeof initMaps === 'function') initMaps(loc.lat, loc.lon); } catch(e){}
                    } else {
                        document.getElementById('locationName').innerHTML = '📍 Unable to determine precise location';
                    }
                }, { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 });
            });
        }
    } catch (e) {
        console.warn('Error attaching high-accuracy refresh handler:', e);
    }
});
