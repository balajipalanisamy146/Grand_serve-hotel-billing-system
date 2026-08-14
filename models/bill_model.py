from extensions import db
from datetime import datetime
import json

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bill_number = db.Column(db.String(20), nullable=False)
    customer_name = db.Column(db.String(100), nullable=True)
    table_number = db.Column(db.String(10), nullable=True)
    items_json = db.Column(db.Text, nullable=False) # Store items as JSON string
    subtotal = db.Column(db.Float, nullable=False)
    gst = db.Column(db.Float, nullable=False)
    grand_total = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), default='Cash')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_items(self):
        return json.loads(self.items_json)

    def to_dict(self):
        return {
            'id': self.id,
            'bill_number': self.bill_number,
            'customer_name': self.customer_name,
            'table_number': self.table_number,
            'items': self.get_items(),
            'subtotal': self.subtotal,
            'gst': self.gst,
            'grand_total': self.grand_total,
            'payment_method': self.payment_method,
            'created_at': self.created_at.isoformat()
        }
