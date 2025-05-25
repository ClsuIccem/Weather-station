import adafruit_dht
import board
import time

# Function to calculate Heat Index
def calculate_heat_index(temperature, humidity):
    # Convert temperature from Celsius to Fahrenheit
    temp_f = (temperature * 9/5) + 32
    
    # Constants for the Heat Index formula
    c1 = -42.379
    c2 = 2.04901523
    c3 = 10.14333127
    c4 = -0.22475541
    c5 = -0.00683783
    c6 = -0.05481717
    c7 = 0.00122874
    c8 = 0.00085282
    c9 = -0.00000199

    # Calculate Heat Index in Fahrenheit
    heat_index_f = (c1 + (c2 * temp_f) + (c3 * humidity) + (c4 * temp_f * humidity) + 
                    (c5 * temp_f**2) + (c6 * humidity**2) + 
                    (c7 * temp_f**2 * humidity) + (c8 * temp_f * humidity**2) +
                    (c9 * temp_f**2 * humidity**2))
    
    # Convert Heat Index back to Celsius
    heat_index_c = (heat_index_f - 32) * 5/9
    return heat_index_c

# Set up the DHT22 sensor on GPIO 4
dht_device = adafruit_dht.DHT22(board.D4)

while True:
    try:
        # Get temperature and humidity
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        
        if temperature is not None and humidity is not None:
            # Calculate Heat Index
            heat_index = calculate_heat_index(temperature, humidity)
            
            # Display the values
            print(f"Temp={temperature:.1f}C  Humidity={humidity:.1f}%  Heat Index={heat_index:.1f}C")
        else:
            print("Failed to retrieve data from the sensor")

    except RuntimeError as error:
        # Handle reading errors (normal for DHT sensors)
        print(error.args[0])
    
    # Wait before taking the next reading
    time.sleep(2)