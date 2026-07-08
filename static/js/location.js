// Location Services for AirPollutionAI
class LocationService {
    constructor() {
        this.watchId = null;
        this.currentLocation = null;
        this.locationHistory = [];
        this.listeners = [];
    }

    // Get current location
    getCurrentLocation(options = {}) {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation not supported'));
                return;
            }

            const defaultOptions = {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            };

            navigator.geolocation.getCurrentPosition(
                position => {
                    this.currentLocation = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: position.timestamp
                    };
                    
                    this.locationHistory.push(this.currentLocation);
                    this.notifyListeners('location', this.currentLocation);
                    
                    resolve(this.currentLocation);
                },
                error => {
                    let message = 'Location error';
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            message = 'Location permission denied';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            message = 'Location unavailable';
                            break;
                        case error.TIMEOUT:
                            message = 'Location timeout';
                            break;
                    }
                    reject(new Error(message));
                },
                { ...defaultOptions, ...options }
            );
        });
    }

    // Start tracking location
    startTracking(options = {}) {
        if (this.watchId) return;

        const defaultOptions = {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        };

        this.watchId = navigator.geolocation.watchPosition(
            position => {
                this.currentLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    timestamp: position.timestamp
                };
                
                this.locationHistory.push(this.currentLocation);
                this.notifyListeners('tracking', this.currentLocation);
            },
            error => console.error('Tracking error:', error),
            { ...defaultOptions, ...options }
        );
    }

    // Stop tracking
    stopTracking() {
        if (this.watchId) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;
        }
    }

    // Calculate distance between two locations (km)
    calculateDistance(loc1, loc2) {
        const R = 6371; // Earth's radius in km
        const dLat = this.toRad(loc2.lat - loc1.lat);
        const dLon = this.toRad(loc2.lng - loc1.lng);
        
        const a = 
            Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(this.toRad(loc1.lat)) * Math.cos(this.toRad(loc2.lat)) * 
            Math.sin(dLon/2) * Math.sin(dLon/2);
        
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    toRad(degrees) {
        return degrees * Math.PI / 180;
    }

    // Add event listener
    addListener(event, callback) {
        this.listeners.push({ event, callback });
    }

    // Notify listeners
    notifyListeners(event, data) {
        this.listeners
            .filter(l => l.event === event)
            .forEach(l => l.callback(data));
    }
}

// Export for use
window.locationService = new LocationService();