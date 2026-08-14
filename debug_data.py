from app import create_app
from models.bill_model import Bill
from models.food_model import Food
from datetime import datetime, timedelta
import json

app = create_app()
with app.app_context():
    print(f"DEBUG START")
    bills = Bill.query.all()
    print(f"Total bills in DB: {len(bills)}")
    
    foods = Food.query.all()
    print(f"Total foods in DB: {len(foods)}")
    
    # Check categories
    cats = set(f.category for f in foods)
    print(f"Categories in DB: {cats}")
    
    # Check today's bills
    now = datetime.utcnow()
    # Let's check a wide range to see what's actually in there
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=24)
    today_bills = Bill.query.filter(Bill.created_at >= today_start).all()
    print(f"Bills since {today_start}: {len(today_bills)}")
    
    for b in today_bills:
        print(f"  Bill {b.bill_number}: Date={b.created_at}, Method={b.payment_method}")
        items = json.loads(b.items_json)
        for item in items:
            food = Food.query.filter_by(name=item['name']).first()
            cat = food.category if food else "NOT FOUND"
            print(f"    - Item: {item['name']}, Cat: {cat}")
    
    print("DEBUG END")
