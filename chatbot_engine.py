import requests
from database import get_db_connection

def fetch_tours():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT title, description, tour_type, price FROM tour_schedules")
    data = cursor.fetchall()
    conn.close()
    return data

def fetch_hotels():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT hotel_name, location, address, room_type_pricing FROM hotels")
    data = cursor.fetchall()
    conn.close()
    return data

def fetch_vehicles():
    try:
        response = requests.get("https://logistic2.easetravelandtours.com/api/vehicle")
        return response.json().get('data', [])
    except Exception as e:
        return [{"error": str(e)}]

def generate_response(message):
    message = message.lower()

    if "tour" in message or "package" in message:
        return {"type": "tours", "data": fetch_tours()}

    elif "hotel" in message or "room" in message:
        return {"type": "hotels", "data": fetch_hotels()}

    elif "car" in message or "vehicle" in message or "bus" in message:
        return {"type": "vehicles", "data": fetch_vehicles()}

    else:
        return {
            "type": "text",
            "data": "I'm sorry, I can assist with available tours, hotels, or vehicles. What would you like to know?"
        }
