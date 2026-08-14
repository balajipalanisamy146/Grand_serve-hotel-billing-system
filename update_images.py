"""
One-time script to update food image URLs in the database to use
high-quality Unsplash photos for all 15 food items.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.food_model import Food

FOOD_IMAGES = {
    "Chicken Briyani":    "https://thumbs.dreamstime.com/b/chicken-dhum-biriyani-using-jeera-rice-spices-arranged-earthen-ware-raitha-lemon-pickle-grey-background-319351621.jpg",
    "Mutton Briyani":     "/static/images/mutton_briyani.png",
    "Veg Fried Rice":     "https://img.freepik.com/premium-photo/photo-delicious-vegetable-rice-plate-isolated-white-background_763111-126913.jpg",
    "Chicken Fried Rice": "https://img.freepik.com/premium-photo/peruvian-chaufa-fried-rice-with-chicken_1179130-45090.jpg?w=2000",
    "Butter Chicken":     "https://static.vecteezy.com/system/resources/previews/025/009/332/large_2x/cilantro-hot-indian-asian-rice-dark-chicken-sauce-masala-traditional-background-generative-ai-photo.jpg",
    "Paneer Butter Masala":"https://i.pinimg.com/originals/09/e4/ac/09e4acfe3778136b196f0202b45f49d5.webp",
    "Tandoori Chicken":   "https://img.freepik.com/premium-photo/tandoori-chicken_670672-7405.jpg",
    "Shawarma":           "https://static.vecteezy.com/system/resources/previews/045/390/535/large_2x/succulent-grilled-shawarma-wrap-teeming-with-fresh-ingredients-a-hearty-meal-anytime-photo.jpeg",
    "Parotta":            "https://thumbs.dreamstime.com/b/homemade-kerala-wheat-paratha-layered-parotta-served-paneer-curry-homemade-kerala-wheat-paratha-layered-parotta-served-320914673.jpg?w=768",
    "Kothu Parotta":      "https://img.freepik.com/premium-photo/chicken-kothu-parotta-curried-shredded-indian-flatbread-popular-south-indian-street-food-made-with-layered-bread-pieces-meat-egg-vegetables-selective-focus_726363-644.jpg?w=2000",
    "Idli":               "https://img.freepik.com/premium-photo/south-indian-famous-breakfast-idly-dosa-ai-generated-images_1277069-13055.jpg",
    "Dosa":               "https://i.pinimg.com/736x/2a/c1/51/2ac15169850a766390adcba3a6d28eef.jpg",
    "Meals":              "https://as2.ftcdn.net/v2/jpg/11/07/77/79/1000_F_1107777935_JtNjYIHV29Rt1YONVEVBakm63OmmKaRa.jpg",
    "Fish Fry":           "https://img.freepik.com/premium-photo/sizzling-delight-grilled-spicy-fish-isolated-white-background_984488-299.jpg",
    "Ice Cream":          "/static/images/ice_cream.jpg",
}

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        updated = 0
        for food in Food.query.all():
            url = FOOD_IMAGES.get(food.name)
            if url:
                food.image_url = url
                updated += 1
        db.session.commit()
        print(f"[OK] Updated {updated} food image URLs successfully!")
        for f in Food.query.all():
            print(f"  [{f.id}] {f.name} -> {f.image_url[:60]}...")
