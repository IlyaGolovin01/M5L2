import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime
import pytz

class DB_Map():
    def __init__(self, database):
        self.database = database
    
    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]  
                cursor.execute('''SELECT * FROM users_cities 
                                 WHERE user_id=? AND city_id=?''', (user_id, city_id))
                if not cursor.fetchone():
                    conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                    conn.commit()
                return 1
            else:
                return 0

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates

    def create_grapf(self, path, cities):
        fig = plt.figure(figsize=(12, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_global()
        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        
        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates:
                lat, lng = coordinates
                plt.plot([lng], [lat], 'ro', markersize=8, transform=ccrs.Geodetic())
                plt.text(lng + 2, lat + 2, city, fontsize=10, 
                        transform=ccrs.Geodetic(), fontweight='bold')
        
        plt.savefig(path, dpi=100, bbox_inches='tight')
        plt.close()

    def get_city_time(self, city_name):
        try:
            coordinates = self.get_coordinates(city_name)
            if not coordinates:
                return None
            
            lat, lng = coordinates
            timezone_offset = int(lng / 15)
            utc_now = datetime.now(pytz.UTC)
            local_time = utc_now + pytz.timedelta(hours=timezone_offset)
            
            return local_time.strftime("%H:%M:%S")
        except Exception as e:
            print(f"Ошибка получения времени: {e}")
            return None
    
    def create_map_with_time(self, path, cities):
        if not cities:
            return False
        
        fig = plt.figure(figsize=(15, 10))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_global()
        ax.add_feature(cfeature.LAND, alpha=0.3)
        ax.add_feature(cfeature.OCEAN, alpha=0.5)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':', alpha=0.5)
        
        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates:
                lat, lng = coordinates
                city_time = self.get_city_time(city)
                
                plt.plot([lng], [lat], 'ro', markersize=10, transform=ccrs.Geodetic())
                
                if city_time:
                    time_text = f"{city}\n{city_time}"
                else:
                    time_text = city
                    
                plt.text(lng + 2, lat + 2, time_text, fontsize=8, 
                        transform=ccrs.Geodetic(), fontweight='bold',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))
        
        plt.title("Карта городов с текущим временем", fontsize=14, fontweight='bold')
        plt.savefig(path, dpi=100, bbox_inches='tight')
        plt.close()
        return True

    def draw_distance(self, city1, city2):
        pass

if __name__=="__main__":
    m = DB_Map(DATABASE)
    m.create_user_table()