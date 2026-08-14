from flask import Blueprint, request, jsonify, session
from extensions import db
from models.user_model import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400
        
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['user'] = user.username
        return jsonify({'success': True, 'message': 'Login successful'})
    
    return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400
        
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    # Seed default data for the new user!
    from database.db import seed_data
    seed_data(user.id)
    
    # Auto log in the user
    session['user_id'] = user.id
    session['user'] = user.username
    
    return jsonify({'success': True, 'message': 'Registration successful'})

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('user', None)
    return jsonify({'success': True, 'message': 'Logged out'})

@auth_bp.route('/check', methods=['GET'])
def check():
    if 'user_id' in session:
        return jsonify({'authenticated': True, 'username': session.get('user')})
    return jsonify({'authenticated': False})
