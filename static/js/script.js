// Update weather data every minute
function updateWeatherData() {
    fetch('/api/weather')
        .then(response => response.json())
        .then(data => {
            document.querySelector('.temperature .number').textContent = data.temperature;
            document.querySelector('.humidity .number').textContent = data.humidity;
            document.querySelector('.pressure .number').textContent = data.pressure;
        })
        .catch(error => console.error('Error fetching weather data:', error));
}

// Update time
function updateTime() {
    const now = new Date();
    // Add any time-related updates here if needed
}

// Initial updates
updateWeatherData();
updateTime();

// Set up periodic updates
setInterval(updateWeatherData, 60000); // Every minute
setInterval(updateTime, 1000); // Every second
