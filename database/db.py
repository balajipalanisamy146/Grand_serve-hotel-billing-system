from extensions import db
from models.food_model import Food
from models.settings_model import Setting



def seed_data(user_id):
    # Define food items without image URLs; they'll be assigned from FOOD_IMAGES
    foods = [
        {"name": "Chicken Briyani", "price": 220, "category": "Non-Veg"},
        {"name": "Mutton Briyani", "price": 320, "category": "Non-Veg"},
        {"name": "Veg Fried Rice", "price": 180, "category": "Veg"},
        {"name": "Chicken Fried Rice", "price": 220, "category": "Non-Veg"},
        {"name": "Butter Chicken", "price": 260, "category": "Non-Veg"},
        {"name": "Paneer Butter Masala", "price": 240, "category": "Veg"},
        {"name": "Tandoori Chicken", "price": 350, "category": "Non-Veg"},
        {"name": "Shawarma", "price": 160, "category": "Non-Veg"},
        {"name": "Parotta", "price": 25, "category": "Veg"},
        {"name": "Kothu Parotta", "price": 180, "category": "Non-Veg"},
        {"name": "Idli", "price": 40, "category": "Veg"},
        {"name": "Dosa", "price": 70, "category": "Veg"},
        {"name": "Meals", "price": 150, "category": "Veg"},
        {"name": "Fish Fry", "price": 280, "category": "Non-Veg"},
        {"name": "Ice Cream", "price": 90, "category": "Dessert"}
    ]


    # Add food entries and assign image URLs
    for f in foods:
        food = Food(user_id=user_id, **f)
        # Assign image URL from mapping if available
        food.image_url = FOOD_IMAGES.get(f["name"], "/static/images/default.jpg")
        db.session.add(food)
    
    # Add default settings
    setting = Setting(user_id=user_id)
    db.session.add(setting)

    db.session.commit()
    print(f"Database seeded successfully for user {user_id}!")
