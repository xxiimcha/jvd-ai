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
def fetch_tours(search=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if search:
        cursor.execute("SELECT id, api_tour_id, title, price, capacity, schedule_date FROM tour_schedules WHERE title LIKE %s LIMIT 5", (f"%{search}%",))
    else:
        cursor.execute("SELECT id, api_tour_id, title, price, capacity, schedule_date FROM tour_schedules LIMIT 5")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Fetch hotels
def fetch_hotels(search=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if search:
        cursor.execute("SELECT id, hotel_name, location, price FROM hotels WHERE hotel_name LIKE %s LIMIT 5", (f"%{search}%",))
    else:
        cursor.execute("SELECT id, hotel_name, location, price FROM hotels LIMIT 5")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Fetch vehicles from external API
def fetch_vehicles(search=None):
    try:
        res = requests.get("https://logistic2.easetravelandtours.com/api/vehicle")
        data = res.json()["data"]
        if search:
            data = [v for v in data if search.lower() in v['model'].lower() or search.lower() in v['vehicle_type'].lower()]
        return data[:5]
    except:
        return []

# Format tours
def format_tours(tours):
    if not tours:
        return "No tours found."
    return "".join([
        f"""
        <div class='chat-result'>
            <strong>{t['title']}</strong><br>
            💰 ₱{t['price']:,.2f} | 👥 Capacity: {t['capacity']} | 📅 {t['schedule_date']}<br>
            <a href='https://core1.easetravelandtours.com/tours/{t['api_tour_id']}' target='_blank'>🔗 View Tour</a>
        </div>
        """ for t in tours
    ])

# Format hotels
def format_hotels(hotels):
    if not hotels:
        return "No hotels found."
    return "".join([
        f"""
        <div class='chat-result'>
            <strong>{h['hotel_name']}</strong><br>
            📍 {h['location']}<br>
            💰 ₱{h['price']:,.2f}<br>
            <a href='https://core1.easetravelandtours.com/hotels/{h['id']}' target='_blank'>🔗 View Hotel</a>
        </div>
        """ for h in hotels
    ])

# Format vehicles
def format_vehicles(vehicles):
    if not vehicles:
        return "No vehicles found."
    return "".join([
        f"""
        <div class='chat-result'>
            <strong>{v['vehicle_type']}</strong><br>
            🚗 {v['model']} | 👥 Capacity: {v['capacity']}<br>
            💰 ₱{v.get('rate', 0):,.2f}<br>
            <img src='https://logistic2.easetravelandtours.com/storage/{v['image_path']}' alt='{v['model']}' style='width:100%; max-width:250px; margin-top:5px; border-radius:8px;'>
        </div>
        """ for v in vehicles
    ])

# Get lowest price from each category
def get_lowest_priced_items():
    tours = fetch_tours()
    hotels = fetch_hotels()
    vehicles = fetch_vehicles()

    lowest_tour = min(tours, key=lambda x: x['price']) if tours else None
    lowest_hotel = min(hotels, key=lambda x: x['price']) if hotels else None
    lowest_vehicle = min(vehicles, key=lambda x: v.get('rate', 0)) if vehicles else None

    sections = []
    if lowest_tour:
        sections.append("<strong>Lowest Tour:</strong><br>" + format_tours([lowest_tour]))
    if lowest_hotel:
        sections.append("<strong>Lowest Hotel:</strong><br>" + format_hotels([lowest_hotel]))
    if lowest_vehicle:
        sections.append("<strong>Lowest Vehicle:</strong><br>" + format_vehicles([lowest_vehicle]))
    return "<hr>".join(sections)

# Generate bot response
def generate_response(message):
    message = message.lower()

    if any(word in message for word in ["cheapest", "lowest", "pinakamura"]):
        return {"reply": get_lowest_priced_items()}

    if any(word in message for word in ["magkano", "price", "presyo", "cost", "amount"]):
        if any(k in message for k in ["tour", "package"]):
            return {"reply": format_tours(fetch_tours())}
        elif any(k in message for k in ["hotel", "room"]):
            return {"reply": format_hotels(fetch_hotels())}
        elif any(k in message for k in ["vehicle", "bus", "van", "car"]):
            return {"reply": format_vehicles(fetch_vehicles())}

    # Search by name for any term
    for category in ["tour", "hotel", "vehicle"]:
        if category in message:
            search_term = message.replace(category, "").strip()
            if category == "tour":
                return {"reply": format_tours(fetch_tours(search_term))}
            elif category == "hotel":
                return {"reply": format_hotels(fetch_hotels(search_term))}
            elif category == "vehicle":
                return {"reply": format_vehicles(fetch_vehicles(search_term))}

    return {"reply": """
        I'm here to help you explore available <strong>tours</strong>, <strong>hotels</strong>, or <strong>vehicles</strong>.<br>
        Try asking things like:<br>
        <em>“Magkano ang bus 6?”</em> or <em>“Show cheapest hotel”</em> or <em>“Tour sa Cebu”</em>
    """}
