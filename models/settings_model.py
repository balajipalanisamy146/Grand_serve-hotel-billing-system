from extensions import db

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hotel_name = db.Column(db.String(100), default='Smart Hotel')
    address = db.Column(db.Text, default='123 Gourmet Street, Food City')
    gst_number = db.Column(db.String(20), default='22AAAAA0000A1Z5')
    tax_percentage = db.Column(db.Float, default=5.0)
    logo_url = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'hotel_name': self.hotel_name,
            'address': self.address,
            'gst_number': self.gst_number,
            'tax_percentage': self.tax_percentage,
            'logo_url': self.logo_url
        }
