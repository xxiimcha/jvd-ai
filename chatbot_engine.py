import mysql.connector
import os
import requests

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE"),
        port=int(os.getenv("DB_PORT", 3306))
    )

# Fetch tours
def fetch_tours():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, api_tour_id, title, price, capacity, schedule_date FROM tour_schedules LIMIT 5")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Fetch hotels
def fetch_hotels():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, hotel_name, location FROM hotels LIMIT 5")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Fetch vehicles from external API
def fetch_vehicles():
    try:
        res = requests.get("https://logistic2.easetravelandtours.com/api/vehicle")
        data = res.json()
        return data["data"][:5]
    except:
        return []

# Format tours with links
def format_tours(tours):
    if not tours:
        return "No tours found."
    return "".join([
        f"""
        <div class='chat-result'>
            <strong>{t['title']}</strong><br>
            💰 ₱{t['price']:.2f} | 👥 Capacity: {t['capacity']} | 📅 {t['schedule_date']}<br>
            <a href='https://core1.easetravelandtours.com/tours/{t['api_tour_id']}' target='_blank'>🔗 View Tour</a>
        </div>
        """ for t in tours
    ])

# Format hotels with links
def format_hotels(hotels):
    if not hotels:
        return "No hotels found."
    return "".join([
        f"""
        <div class='chat-result'>
            <strong>{h['hotel_name']}</strong><br>
            📍 {h['location']}<br>
            <a href='https://core1.easetravelandtours.com/hotels/{h['id']}' target='_blank'>🔗 View Hotel</a>
        </div>
        """ for h in hotels
    ])

# Format vehicles with image
def format_vehicles(vehicles):
    if not vehicles:
        return "No vehicles found."
    return "".join([
        f"""
        <div class='chat-result'>
            <strong>{v['vehicle_type']}</strong><br>
            🚗 {v['model']} | 👥 Capacity: {v['capacity']}<br>
            <img src="https://logistic2.easetravelandtours.com/storage/{v['image_path']}" 
                 alt="{v['model']}" 
                 style="width:100%; max-width:250px; margin-top:5px; border-radius:8px;">
        </div>
        """ for v in vehicles
    ])

# Generate bot response
def generate_response(message):
    message = message.lower()
    if "tour" in message:
        return {"reply": format_tours(fetch_tours())}
    elif "hotel" in message:
        return {"reply": format_hotels(fetch_hotels())}
    elif "vehicle" in message or "car" in message:
        return {"reply": format_vehicles(fetch_vehicles())}
    else:
        return {"reply": """
        I'm sorry, I can help you with available <strong>tours</strong>, <strong>hotels</strong>, or <strong>vehicles</strong>.<br>
        <em>What would you like to know?</em>
        """}
