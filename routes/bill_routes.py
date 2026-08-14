from flask import Blueprint, request, jsonify, session
from extensions import db
from models.bill_model import Bill
from models.food_model import Food
import json
from datetime import datetime

bill_bp = Blueprint('bills', __name__)

@bill_bp.route('/', methods=['GET'])
def get_bills():
    bills = Bill.query.filter_by(user_id=session['user_id']).order_by(Bill.created_at.desc()).all()
    return jsonify([b.to_dict() for b in bills])

@bill_bp.route('/foods', methods=['GET'])
def get_foods():
    foods = Food.query.filter_by(user_id=session['user_id'], available=True).all()
    return jsonify([f.to_dict() for f in foods])

@bill_bp.route('/save', methods=['POST'])
def save_bill():
    data = request.get_json()
    
    # Generate bill number (e.g., BILL-20260513-001) scoped to this user
    today_str = datetime.now().strftime('%Y%m%d')
    last_bill = Bill.query.filter(
        Bill.user_id == session['user_id'],
        Bill.bill_number.like(f"BILL-{today_str}-%")
    ).order_by(Bill.id.desc()).first()
    
    if last_bill:
        try:
            last_num = int(last_bill.bill_number.split('-')[-1])
            bill_count = last_num + 1
        except:
            bill_count = 1
    else:
        bill_count = 1
        
    bill_number = f"BILL-{today_str}-{bill_count:03d}"
    
    new_bill = Bill(
        user_id=session['user_id'],
        bill_number=bill_number,
        customer_name=data.get('customer_name'),
        table_number=data.get('table_number'),
        items_json=json.dumps(data.get('items')),
        subtotal=data.get('subtotal'),
        gst=data.get('gst'),
        grand_total=data.get('grand_total'),
        payment_method=data.get('payment_method', 'Cash')
    )
    
    db.session.add(new_bill)
    db.session.commit()
    
    return jsonify({'success': True, 'bill': new_bill.to_dict()}), 201

@bill_bp.route('/<int:bill_id>', methods=['DELETE'])
def delete_bill(bill_id):
    bill = Bill.query.filter_by(id=bill_id, user_id=session['user_id']).first_or_404()
    db.session.delete(bill)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Bill deleted'})
