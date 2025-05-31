import mysql.connector
import os
import requests


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE"),
        port=int(os.getenv("DB_PORT", 3306))
    )

def fetch_tours():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT title, price, capacity, schedule_date FROM tour_schedules LIMIT 5")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def fetch_hotels():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT hotel_name, location FROM hotels LIMIT 5")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def fetch_vehicles():
    try:
        res = requests.get("https://logistic2.easetravelandtours.com/api/vehicle")
        data = res.json()
        return data["data"][:5]
    except:
        return []

def format_tours(tours):
    if not tours:
        return "No tours found."
    return "\n".join([f"{t['title']} - ₱{t['price']:.2f} - Capacity: {t['capacity']} - Date: {t['schedule_date']}" for t in tours])

def format_hotels(hotels):
    if not hotels:
        return "No hotels found."
    return "\n".join([f"{h['hotel_name']} - {h['location']}" for h in hotels])

def format_vehicles(vehicles):
    if not vehicles:
        return "No vehicles found."
    return "\n".join([f"{v['vehicle_type']} - {v['model']} - Capacity: {v['capacity']}" for v in vehicles])

def generate_response(message):
    message = message.lower()
    if "tour" in message:
        return {"reply": format_tours(fetch_tours())}
    elif "hotel" in message:
        return {"reply": format_hotels(fetch_hotels())}
    elif "vehicle" in message or "car" in message:
        return {"reply": format_vehicles(fetch_vehicles())}
    else:
        return {"reply": "I'm sorry, I can help you with available tours, hotels, or vehicles. What would you like to know?"}
