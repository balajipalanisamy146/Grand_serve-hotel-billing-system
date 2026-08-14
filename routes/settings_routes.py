from flask import Blueprint, request, jsonify, session
from extensions import db
from models.settings_model import Setting
from models.food_model import Food

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/', methods=['GET'])
def get_settings():
    setting = Setting.query.filter_by(user_id=session['user_id']).first()
    if not setting:
        setting = Setting(user_id=session['user_id'])
        db.session.add(setting)
        db.session.commit()
    return jsonify(setting.to_dict())

@settings_bp.route('/', methods=['POST'])
def update_settings():
    data = request.get_json()
    setting = Setting.query.filter_by(user_id=session['user_id']).first()
    
    if not setting:
        setting = Setting(user_id=session['user_id'])
        db.session.add(setting)
        
    setting.hotel_name = data.get('hotel_name', setting.hotel_name)
    setting.address = data.get('address', setting.address)
    setting.gst_number = data.get('gst_number', setting.gst_number)
    setting.tax_percentage = data.get('tax_percentage', setting.tax_percentage)
    setting.logo_url = data.get('logo_url', setting.logo_url)
    
    db.session.commit()
    return jsonify({'success': True, 'settings': setting.to_dict()})

@settings_bp.route('/food', methods=['GET'])
def get_all_foods():
    foods = Food.query.filter_by(user_id=session['user_id']).order_by(Food.id.desc()).all()
    return jsonify([f.to_dict() for f in foods])

@settings_bp.route('/food', methods=['POST'])
def add_food():
    data = request.get_json()
    new_food = Food(
        user_id=session['user_id'],
        name=data.get('name'),
        price=float(data.get('price')),
        category=data.get('category'),
        image_url=data.get('image_url')
    )
    db.session.add(new_food)
    db.session.commit()
    return jsonify({'success': True, 'food': new_food.to_dict()})

@settings_bp.route('/food/<int:food_id>', methods=['DELETE'])
def delete_food(food_id):
    food = Food.query.filter_by(id=food_id, user_id=session['user_id']).first_or_404()
    db.session.delete(food)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Dish deleted successfully'})

@settings_bp.route('/food/<int:food_id>', methods=['PUT'])
def update_food(food_id):
    data = request.get_json()
    food = Food.query.filter_by(id=food_id, user_id=session['user_id']).first_or_404()
    
    food.name = data.get('name', food.name)
    food.price = float(data.get('price', food.price))
    food.category = data.get('category', food.category)
    food.image_url = data.get('image_url', food.image_url)
    
    db.session.commit()
    return jsonify({'success': True, 'food': food.to_dict()})
