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

    keywords = {
        "tour": ["tour", "package", "tour price"],
        "hotel": ["hotel", "room", "accommodation"],
        "vehicle": ["vehicle", "bus", "car", "van", "service", "jeep"]
    }

    # Smart keyword + price/amount trigger
    if any(word in message for word in ["magkano", "price", "presyo", "cost", "amount"]):
        if any(k in message for k in keywords["tour"]):
            return {"reply": format_tours(fetch_tours())}
        elif any(k in message for k in keywords["hotel"]):
            return {"reply": format_hotels(fetch_hotels())}
        elif any(k in message for k in keywords["vehicle"]):
            return {"reply": format_vehicles(fetch_vehicles())}
        else:
            return {"reply": """
                I noticed you're asking about pricing. Please clarify if you're referring to a <strong>tour</strong>, <strong>hotel</strong>, or <strong>vehicle</strong>.<br>
                Example: <em>“Magkano po ang bus?”</em> or <em>“Tour package price”</em>
            """}
    elif "tour" in message:
        return {"reply": format_tours(fetch_tours())}
    elif "hotel" in message:
        return {"reply": format_hotels(fetch_hotels())}
    elif "vehicle" in message or "car" in message:
        return {"reply": format_vehicles(fetch_vehicles())}
    else:
        return {"reply": """
            I'm here to help you explore available <strong>tours</strong>, <strong>hotels</strong>, or <strong>vehicles</strong>.<br>
            Try asking something like: <em>“Show me hotel options in Baguio”</em> or <em>“Magkano po ang tour sa Cebu?”</em>
        """}
