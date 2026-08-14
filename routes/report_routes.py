from flask import Blueprint, jsonify, session
from extensions import db
from models.bill_model import Bill
from sqlalchemy import func
from datetime import datetime, timedelta
from models.food_model import Food

report_bp = Blueprint('reports', __name__)

@report_bp.route('/daily', methods=['GET'])
def daily_report():
    # Filter for last 24 hours to be timezone-safe, or start of local day
    # For now, let's use a generous window for "today" to ensure nothing is missed
    # Daily timeframe (24h buffer for IST/UTC)
    """now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=6)"""
    
    now_utc = datetime.utcnow()
    now_ist = now_utc + timedelta(hours=5, minutes=30)
    today_ist_start = now_ist.replace(hour=0, minute=0, second=0, microsecond=0)
    today_start = today_ist_start - timedelta(hours=5, minutes=30)

    bills = Bill.query.filter(Bill.user_id == session['user_id'], Bill.created_at >= today_start).all()
    
    total_sales = 0
    num_bills = 0
    
    # Calculate product-wise sales and payment breakdown
    product_stats = {}
    payments = {'Cash': 0, 'UPI': 0, 'Card': 0}
    
    for b in bills:
        total_sales += (b.grand_total or 0)
        num_bills += 1
        
        # Payments
        method = (b.payment_method or 'Cash').capitalize()
        if method in payments:
            payments[method] += (b.grand_total or 0)
        elif 'Upi' in method:
            payments['UPI'] += (b.grand_total or 0)
        else:
            payments['Cash'] += (b.grand_total or 0)
            
        items = b.get_items()
        for item in items:
            name = str(item.get('name', 'Unknown')).strip()
            qty = float(item.get('quantity', 0))
            price = float(item.get('price', 0))
            
            if name not in product_stats:
                product_stats[name] = {'qty': 0, 'revenue': 0}
            product_stats[name]['qty'] += qty
            product_stats[name]['revenue'] += (qty * price)
    
    all_foods = Food.query.filter_by(user_id=session['user_id']).all()
    food_cat_map = {f.name.strip(): f.category for f in all_foods}
    
    # Calculate Category Sales
    category_sales = {'Veg': 0, 'Non-Veg': 0, 'Dessert': 0}
    for name, stats in product_stats.items():
        name_clean = name.strip()
        raw_cat = (food_cat_map.get(name_clean) or '').strip().lower()
        
        if 'non' in raw_cat:
            cat = 'Non-Veg'
        elif 'veg' in raw_cat:
            cat = 'Veg'
        elif 'dessert' in raw_cat or 'sweet' in raw_cat:
            cat = 'Dessert'
        else:
            cat = 'Other'
            
        category_sales[cat] = category_sales.get(cat, 0) + stats['revenue']
    
    # Best selling logic
    detailed_food_sales = []
    for food in all_foods:
        stats = product_stats.get(food.name, {'qty': 0, 'revenue': 0})
        detailed_food_sales.append({
            'name': food.name,
            'qty': stats['qty'],
            'revenue': stats['revenue'],
            'image': food.image_url
        })
    detailed_food_sales.sort(key=lambda x: x['qty'], reverse=True)
    best_selling = detailed_food_sales[0]['name'] if detailed_food_sales else "N/A"

    return jsonify({
        'total_sales': total_sales,
        'num_bills': num_bills,
        'best_selling': best_selling,
        'avg_order_value': total_sales / num_bills if num_bills > 0 else 0,
        'food_sales': detailed_food_sales,
        'payments': payments,
        'category_sales': category_sales
    })

@report_bp.route('/analytics', methods=['GET'])
def analytics_data():
    # Last 7 days sales for chart
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=6)
    
    results = db.session.query(
        func.date(Bill.created_at).label('date'),
        func.sum(Bill.grand_total).label('total')
    ).filter(
        Bill.user_id == session['user_id'],
        Bill.created_at >= start_date
    ).group_by(func.date(Bill.created_at)).all()
    
    chart_data = {str(r.date): r.total for r in results}
    
    # Fill in missing dates
    all_dates = {}
    for i in range(7):
        d = start_date + timedelta(days=i)
        all_dates[str(d)] = chart_data.get(str(d), 0)
        
    return jsonify({
        'labels': list(all_dates.keys()),
        'values': list(all_dates.values())
    })
