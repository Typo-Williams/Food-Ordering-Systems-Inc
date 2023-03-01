from datetime import datetime
from app import db
from flask_login import UserMixin
class Customer(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50),unique=True)
    phone = db.Column(db.String(20))
    user_password = db.Column(db.String(50))
    role=db.Column(db.Integer,default=1) # 1 for user, 2 for admin
    # Relationship to Order
    orders = db.relationship('Order', backref='customer', lazy=True)
    
    def get_id(self):
        return self.email
    #checking if user is admin or not
    def is_admin(self):
        return self.role == 2
     

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    order_time = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationship to OrderItem
    order_items = db.relationship('OrderItem', backref='order', lazy=True)
    
class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    price = db.Column(db.Float)
    category=db.Column(db.String(50))
    

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.Integer, db.ForeignKey('food.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    total_price = db.Column(db.Float)
    # Relationship to Food
    food = db.relationship('Food', backref='order_items', lazy=True)

