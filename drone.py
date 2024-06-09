import folium
import random
import time
import threading
from flask import Flask
import logging

app = Flask(__name__)

class Drone:
    def __init__(self, name, latitude, longitude):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.battery_status = 100
        self.needs_attention = False

    def update_location(self):
        self.latitude += random.uniform(-0.01, 0.01)
        self.longitude += random.uniform(-0.01, 0.01)

    def update_battery_status(self):
        self.battery_status -= random.uniform(15, 10)
        if self.battery_status < 0:
            self.battery_status = 0
        if self.battery_status < 20 and not self.needs_attention:
            self.needs_attention = True
            logging.warning(f"{self.name} needs attention! Battery level: {self.battery_status}%")

    def get_info(self):
        return f"Name: {self.name}, Location: ({self.latitude}, {self.longitude}), Battery Status: {self.battery_status}%"

class DroneFleet:
    def __init__(self):
        self.drones = []
        self.map = folium.Map(location=[40.7128, -74.0060], zoom_start=12)
        self.map.save("drones_map.html")

    def add_drone(self, drone):
        self.drones.append(drone)

    def update_drones(self):
        while True:
            try:
                for drone in self.drones:
                    drone.update_location()
                    drone.update_battery_status()
                    logging.info(drone.get_info())
                    if drone.needs_attention:
                        folium.Marker([drone.latitude, drone.longitude], popup=f"{drone.name} - Battery: {drone.battery_status}%", icon=folium.Icon(color='red')).add_to(self.map)
                    else:
                        folium.Marker([drone.latitude, drone.longitude], popup=f"{drone.name} - Battery: {drone.battery_status}%").add_to(self.map)
                self.map.save("drones_map.html")
                time.sleep(5)
            except Exception as e:
                logging.error(f"Error updating drones: {str(e)}")

@app.route('/')
def index():
    return open('drones_map.html').read()

def main():
    fleet = DroneFleet()
    for i in range(5):
        drone = Drone(f"Drone {i}", 40.7128, -74.0060)
        fleet.add_drone(drone)

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    threading.Thread(target=fleet.update_drones).start()

    app.run(port=0000)

if __name__ == "__main__":
    main()
