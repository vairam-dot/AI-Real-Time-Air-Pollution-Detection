// Manual search integration for Tamil Nadu
// Shows multiple matches, allows selecting result to center map and display AQI circle/marker

(function(){
  const input = document.getElementById('manual-search-input');
  const btn = document.getElementById('manual-search-btn');
  const status = document.getElementById('manual-search-status');

  // Create results container under input if not present
  let resultsContainer = document.getElementById('manual-search-results');
  if (!resultsContainer) {
    resultsContainer = document.createElement('div');
    resultsContainer.id = 'manual-search-results';
    resultsContainer.style.marginTop = '8px';
    resultsContainer.style.maxHeight = '240px';
    resultsContainer.style.overflowY = 'auto';
    resultsContainer.style.background = '#fff';
    resultsContainer.style.border = '1px solid #e6e6e6';
    resultsContainer.style.padding = '6px';
    resultsContainer.style.borderRadius = '6px';
    const parent = input.parentNode || document.body;
    parent.insertBefore(resultsContainer, input.nextSibling);
  }

  // Hold markers/circles so we can clear them
  window.manualSearchMarkers = window.manualSearchMarkers || [];

  function clearMarkers() {
    if (!window.manualSearchMarkers) return;
    window.manualSearchMarkers.forEach(m => {
      try { m.marker && m.marker.remove(); } catch(e){}
      try { m.circle && m.circle.remove(); } catch(e){}
    });
    window.manualSearchMarkers = [];
  }

  function getCategoryColor(aqi) {
    // aqi numeric expected
    if (aqi === null || aqi === undefined || isNaN(aqi)) return '#999';
    aqi = Number(aqi);
    if (aqi <= 50) return '#4CAF50';
    if (aqi <= 100) return '#ff9800';
    if (aqi <= 150) return '#ffc107';
    if (aqi <= 200) return '#f44336';
    if (aqi <= 300) return '#9c27b0';
    return '#7b1fa2';
  }

  function createResultItem(r, idx) {
    const div = document.createElement('div');
    div.style.padding = '6px';
    div.style.borderBottom = '1px solid #f1f1f1';
    div.style.display = 'flex';
    div.style.justifyContent = 'space-between';
    div.style.alignItems = 'center';

    const left = document.createElement('div');
    left.style.flex = '1';
    left.style.marginRight = '8px';
    left.innerHTML = `<div style="font-weight:600;">${r.name || 'Unknown'}</div>
                      <div style="font-size:0.85rem;color:#666">${r.lat.toFixed(5)}, ${r.lon.toFixed(5)}</div>`;

    const aqiVal = (r.aqi && (r.aqi.aqi !== undefined)) ? r.aqi.aqi : (r.aqi || 'N/A');
    const right = document.createElement('div');
    right.style.display = 'flex';
    right.style.flexDirection = 'column';
    right.style.alignItems = 'flex-end';
    right.innerHTML = `<div style="font-weight:600">AQI: ${aqiVal}</div>`;

    const btnShow = document.createElement('button');
    btnShow.textContent = 'Show';
    btnShow.style.marginTop = '6px';
    btnShow.className = 'btn';
    btnShow.style.padding = '4px 8px';
    btnShow.style.border = '1px solid #ddd';
    btnShow.style.background = '#fff';
    btnShow.style.cursor = 'pointer';

    btnShow.addEventListener('click', function(){
      // center map and add marker + colored circle
      const lat = r.lat; const lon = r.lon;
      const color = getCategoryColor(aqiVal);

      const targetMap = window.map || (typeof map !== 'undefined' && map) || null;
      if (!targetMap || typeof L === 'undefined') {
        status.textContent = 'Map not ready.';
        return;
      }

      targetMap.setView([lat, lon], 12);

      // Clear previous markers but keep other manualSearchMarkers if user wants multiple
      clearMarkers();

      const marker = L.marker([lat, lon]).addTo(targetMap)
        .bindPopup(`<strong>${r.name || 'Location'}</strong><br/>AQI: ${aqiVal}`).openPopup();

      const circle = L.circle([lat, lon], {
        color: color,
        fillColor: color,
        fillOpacity: 0.15,
        radius: 5000
      }).addTo(targetMap);

      window.manualSearchMarkers.push({ marker, circle });
      // update dashboard location label if available
      try {
        const locLabel = document.getElementById('locationName');
        if (locLabel) locLabel.innerHTML = `📍 ${r.name || (lat.toFixed(4) + ', ' + lon.toFixed(4))}`;
      } catch (e) {}

      // Fetch nearby pollution stations from IQAir (WAQI) for this location
      fetchNearbyStationsForLocation(lat, lon, targetMap);
      
      // Also fetch weather and pollutant data for this location
      fetchAqiDataForLocation(lat, lon);
      
      // emit socket event to request dashboard update for this location
      try {
        if (window.socket && typeof window.socket.emit === 'function') {
          window.socket.emit('request_update', { lat: lat, lon: lon });
        }
      } catch (e) {}
      
      // Also update AQI History chart for this location
      updateAQIHistoryForLocation(lat, lon);
      
      // Update global currentLat/currentLon for dashboard
      if (typeof currentLat !== 'undefined') {
        currentLat = lat;
        currentLon = lon;
      }
    });
    
    // Function to update AQI History chart when location changes
    function updateAQIHistoryForLocation(lat, lon) {
      // Call the dashboard's fetchAQIHistory function if it exists
      if (typeof window.fetchAQIHistory === 'function') {
        // Update currentLat/currentLon in global scope
        if (typeof currentLat !== 'undefined') {
          currentLat = lat;
          currentLon = lon;
        }
        
        // Call the history function
        window.fetchAQIHistory('hour');
      } else {
        // Fallback: directly fetch from API
        fetchAQIHistoryDirect(lat, lon, 'hour');
      }
    }
    
    // Direct fetch for AQI history (fallback)
    function fetchAQIHistoryDirect(lat, lon, range) {
      const hoursMap = { 'hour': 1, 'day': 24, 'week': 168, 'month': 720 };
      const hours = hoursMap[range] || 24;
      
      // Try local API first
      fetch(`/api/aqi-history?lat=${lat}&lon=${lon}&hours=${hours}`)
        .then(res => res.json())
        .then(data => {
          if (data.records && data.records.length > 0 && typeof aqiChart !== 'undefined') {
            const labels = data.records.map(r => {
              const date = new Date(r.recorded_at);
              if (range === 'hour') return date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
              if (range === 'day') return date.toLocaleTimeString([], {hour: '2-digit'});
              return date.toLocaleDateString([], {month: 'short', day: 'numeric'});
            }).reverse();
            const values = data.records.map(r => r.aqi).reverse();
            
            if (aqiChart) {
              aqiChart.data.labels = labels;
              aqiChart.data.datasets[0].data = values;
              aqiChart.update();
            }
          } else {
            // Fallback to Open-Meteo
            fetchOpenMeteoHistory(lat, lon, hours, range);
          }
        })
        .catch(err => {
          fetchOpenMeteoHistory(lat, lon, hours, range);
        });
    }
    
    // Fetch from Open-Meteo API
    function fetchOpenMeteoHistory(lat, lon, hours, range) {
      fetch(`https://air-quality-api.open-meteo.com/v1/air-quality?latitude=${lat}&longitude=${lon}&hourly=us_aqi&forecast_days=${Math.ceil(hours/24)}`)
        .then(res => res.json())
        .then(data => {
          if (data.hourly && data.hourly.us_aqi && typeof aqiChart !== 'undefined') {
            const aqiValues = data.hourly.us_aqi.slice(0, hours);
            const times = data.hourly.time.slice(0, hours);
            
            const labels = times.map(t => {
              const date = new Date(t);
              if (hours <= 24) return date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
              return date.toLocaleDateString([], {month: 'short', day: 'numeric'});
            });
            
            if (aqiChart) {
              aqiChart.data.labels = labels;
              aqiChart.data.datasets[0].data = aqiValues;
              aqiChart.update();
            }
          }
        })
        .catch(err => console.log('Open-Meteo history error:', err));
    }
    
    // Function to fetch and display nearby pollution stations
    function fetchNearbyStationsForLocation(lat, lon, targetMap) {
      fetch(`/api/nearby-stations?lat=${lat}&lon=${lon}&limit=10`)
        .then(res => res.json())
        .then(data => {
          if (data.stations && data.stations.length > 0) {
            data.stations.forEach(station => {
              if (station.lat && station.lon && station.aqi) {
                const stationColor = getCategoryColor(parseInt(station.aqi));
                
                L.circleMarker([station.lat, station.lon], {
                  color: stationColor,
                  fillColor: stationColor,
                  fillOpacity: 0.8,
                  radius: 10
                }).addTo(targetMap).bindPopup(
                  `<strong>${station.name || 'Station'}</strong><br/>` +
                  `AQI: ${station.aqi}`
                );
              }
            });
            console.log(`Loaded ${data.count} stations from IQAir for searched location`);
          }
        })
        .catch(err => console.log('Station fetch error:', err));
    }
    
    // Function to fetch AQI data for location
    function fetchAqiDataForLocation(lat, lon) {
      fetch(`/api/current-aqi?lat=${lat}&lon=${lon}`)
        .then(res => res.json())
        .then(data => {
          // Update pollutant bars if available
          if (data.components) {
            updatePollutantBarsFromSearch(data.components);
          }
          // Update weather if available
          if (data.weather) {
            updateWeatherFromSearch(data.weather);
          }
        })
        .catch(err => console.log('AQI fetch error:', err));
    }
    
    // Update pollutant bars in dashboard
    function updatePollutantBarsFromSearch(components) {
      if (!components) return;
      
      // PM2.5
      const pm25 = components.pm2_5 || 0;
      const pm25BarValue = document.getElementById('pm25BarValue');
      const pm25BarFill = document.getElementById('pm25BarFill');
      if (pm25BarValue) pm25BarValue.textContent = pm25 + ' µg/m³';
      if (pm25BarFill) pm25BarFill.style.width = Math.min(100, (pm25 / 75) * 100) + '%';
      
      // PM10
      const pm10 = components.pm10 || 0;
      const pm10BarValue = document.getElementById('pm10BarValue');
      const pm10BarFill = document.getElementById('pm10BarFill');
      if (pm10BarValue) pm10BarValue.textContent = pm10 + ' µg/m³';
      if (pm10BarFill) pm10BarFill.style.width = Math.min(100, (pm10 / 150) * 100) + '%';
      
      // NO2
      const no2 = components.no2 || 0;
      const no2BarValue = document.getElementById('no2BarValue');
      const no2BarFill = document.getElementById('no2BarFill');
      if (no2BarValue) no2BarValue.textContent = no2 + ' ppb';
      if (no2BarFill) no2BarFill.style.width = Math.min(100, (no2 / 100) * 100) + '%';
      
      // SO2
      const so2 = components.so2 || 0;
      const so2BarValue = document.getElementById('so2BarValue');
      const so2BarFill = document.getElementById('so2BarFill');
      if (so2BarValue) so2BarValue.textContent = so2 + ' ppb';
      if (so2BarFill) so2BarFill.style.width = Math.min(100, (so2 / 80) * 100) + '%';
      
      // O3
      const o3 = components.o3 || 0;
      const o3BarValue = document.getElementById('o3BarValue');
      const o3BarFill = document.getElementById('o3BarFill');
      if (o3BarValue) o3BarValue.textContent = o3 + ' ppb';
      if (o3BarFill) o3BarFill.style.width = Math.min(100, (o3 / 180) * 100) + '%';
      
      // CO
      const co = components.co || 0;
      const coBarValue = document.getElementById('coBarValue');
      const coBarFill = document.getElementById('coBarFill');
      if (coBarValue) coBarValue.textContent = co + ' ppm';
      if (coBarFill) coBarFill.style.width = Math.min(100, (co / 10) * 100) + '%';
      
      // Update timestamp
      const updateTime = document.getElementById('pollutantUpdateTime');
      if (updateTime) updateTime.textContent = 'Updated: ' + new Date().toLocaleTimeString();
    }
    
    // Update weather in dashboard
    function updateWeatherFromSearch(weather) {
      if (!weather) return;
      
      const weatherTemp = document.getElementById('weatherTemp');
      const weatherHumidity = document.getElementById('weatherHumidity');
      const weatherWind = document.getElementById('weatherWind');
      const weatherPressure = document.getElementById('weatherPressure');
      const weatherVisibility = document.getElementById('weatherVisibility');
      const weatherUV = document.getElementById('weatherUV');
      
      if (weatherTemp) weatherTemp.textContent = weather.temperature + '°C';
      if (weatherHumidity) weatherHumidity.textContent = weather.humidity + '%';
      if (weatherWind) weatherWind.textContent = weather.wind_speed + ' km/h';
      if (weatherPressure) weatherPressure.textContent = weather.pressure + ' hPa';
      if (weatherVisibility) weatherVisibility.textContent = (weather.visibility || '--') + ' km';
      if (weatherUV) weatherUV.textContent = weather.uv_index || '--';
    }

    right.appendChild(btnShow);
    div.appendChild(left);
    div.appendChild(right);
    return div;
  }

  async function doSearch() {
    const q = input.value.trim();
    if (!q) {
      status.textContent = 'Please enter a place or coordinates.';
      return;
    }
    // If user entered numeric coords (lat,lon), try reverse-geocoding to a Tamil Nadu place name first
    const coordMatch = q.match(/^\s*([-+]?\d+(?:\.\d+)?)\s*,\s*([-+]?\d+(?:\.\d+)?)\s*$/);
    let searchQuery = q;
    if (coordMatch) {
      const lat = parseFloat(coordMatch[1]);
      const lon = parseFloat(coordMatch[2]);
      status.textContent = 'Resolving coordinates to place...';
      try {
        const params = new URLSearchParams({ lat: lat, lon: lon, format: 'json', zoom: 10, addressdetails: 1 });
        const resp = await fetch(`https://nominatim.openstreetmap.org/reverse?${params.toString()}`, {
          headers: { 'User-Agent': 'AirPollutionAI/1.0 (contact@localhost)' }
        });
        if (resp.ok) {
          const data = await resp.json();
          // Prefer locality within Tamil Nadu; fallback to display_name
          const addr = data.address || {};
          let place = null;
          if (addr.state && addr.state.toLowerCase().includes('tamil')) {
            if (addr.city) place = addr.city;
            else if (addr.town) place = addr.town;
            else if (addr.village) place = addr.village;
            else place = data.display_name;
          } else {
            // If reverse result is outside Tamil Nadu, still try a forward search within Tamil Nadu
            place = null;
          }

          if (place) {
            searchQuery = `${place}, Tamil Nadu, India`;
            // update input to show resolved place
            input.value = searchQuery;
          } else {
            // If not in Tamil Nadu or reverse failed, fallback to using the coordinate string as-is
            searchQuery = `${lat},${lon}`;
          }
        }
      } catch (err) {
        // ignore and fallback to coords
        searchQuery = `${lat},${lon}`;
      }
    }

    status.textContent = 'Searching...';
    resultsContainer.innerHTML = '';
    clearMarkers();

    try {
      const res = await fetch(`/api/manual-search?q=${encodeURIComponent(searchQuery)}`);
      if (!res.ok) {
        const body = await res.json().catch(()=>({message: res.statusText}));
        status.textContent = body.message || body.error || 'No results';
        return;
      }

      const body = await res.json();
      if (!body.results || body.results.length === 0) {
        status.textContent = 'No matches found.';
        return;
      }

      status.textContent = `Found ${body.results.length} result(s)`;

      // render results
      body.results.forEach((r, i) => {
        const item = createResultItem(r, i);
        resultsContainer.appendChild(item);
      });

    } catch (err) {
      status.textContent = 'Error: ' + (err.message || err);
    }
  }

  btn.addEventListener('click', doSearch);
  input.addEventListener('keypress', function(e){ if (e.key === 'Enter') doSearch(); });
})();
