from app import app
from models.bill_model import Bill
from models.food_model import Food
from datetime import datetime, timedelta
import json

with app.app_context():
    print(f"Current UTC: {datetime.utcnow()}")
    bills = Bill.query.order_by(Bill.created_at.desc()).limit(10).all()
    if not bills:
        print("No bills found in database.")
    for b in bills:
        print(f"Bill: {b.bill_number}, Total: {b.grand_total}, Date: {b.created_at}")
        items = json.loads(b.items_json)
        for item in items:
            food = Food.query.filter_by(name=item['name']).first()
            cat = food.category if food else "NOT FOUND"
            print(f"  - Item: {item['name']}, Cat: {cat}")
    
    foods = Food.query.all()
    cats = {}
    for f in foods:
        cats[f.category] = cats.get(f.category, 0) + 1
    print(f"Categories count: {cats}")
