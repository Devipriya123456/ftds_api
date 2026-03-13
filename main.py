from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345678@localhost/product_db'

db = SQLAlchemy(app)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serviceId = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    userId = db.Column(db.Integer, nullable=False)
    deleteStatus = db.Column(db.Boolean, default=False)
    status= db.Column(db.String(20), default='inCart')
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    deleteAt= db.Column(db.DateTime, nullable=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cartId = db.Column(db.Integer, nullable=False)
    userId = db.Column(db.Integer, nullable=False)
    paymentStatus = db.Column(db.String(20), default='pending')
    deleteStatus = db.Column(db.Boolean, default=False)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    deleteAt= db.Column(db.DateTime, nullable=True)

with app.app_context():
    db.create_all()

@app.route('/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    serviceId = data.get('serviceId')
    quantity = data.get('quantity')
    userId = data.get('userId')

    if not serviceId or not quantity or not userId:
        return jsonify({'error': 'Missing required fields'}), 400
    
    existing_cart = Cart.query.filter(
    Cart.userId == userId,
    Cart.deleteStatus == False
).first()

    if existing_cart:
       return {"message": "User already has cart"}
        
    new_cart_item = Cart(serviceId=serviceId, quantity=quantity, userId=userId)
    db.session.add(new_cart_item)
    db.session.commit()

    return jsonify({'message': 'Item added to cart successfully'}), 201

@app.route('/cart/updatebyUserId/<int:userId>', methods=['PUT'])
def update_cart_by_user_id(userId):
    data = request.get_json()
    quantity = data.get('quantity')

    if not userId or not quantity:
        return jsonify({'error': 'Missing required fields'}), 400

    cart = Cart.query.filter(
        Cart.userId == userId,
        Cart.deleteStatus == False
    ).first()

    if not cart:
        return jsonify({'error': 'Cart item not found'}), 404

    cart.quantity = quantity
    db.session.commit()

    return jsonify({'message': 'Cart updated successfully'}), 200

@app.route('/cart/increase/<int:id>', methods=['PUT'])
def increse_quantity(id):
    cart = Cart.query.get(id)
    if not cart:
        return jsonify({'error': 'Cart item not found'}), 404
    
    
    cart.quantity += 1
           
          
    db.session.commit()

    return jsonify({'message': 'Quantity increased successfully'}), 200

@app.route('/cart/decrease/<int:id>', methods=['PUT'])
def decrease_quantity(id):
    cart = Cart.query.get(id)
    if not cart:
        return jsonify({'error': 'Cart item not found'}), 404
    
    if cart.quantity >= 1:
        cart.quantity -= 1
           
          
    db.session.commit()

    return jsonify({'message': 'Quantity decreased successfully'}), 200

@app.route('/cart/<int:id>', methods=['GET'])
def get_cart_item(id):
    cart = Cart.query.get(id)
    if not cart:
        return jsonify({'error': 'Cart item not found'}), 404
    
    cart_data = {
        'id': cart.id,
        'serviceId': cart.serviceId,
        'quantity': cart.quantity,
        'userId': cart.userId,
        'deleteStatus': cart.deleteStatus,
        'status': cart.status,
        'createdAt': cart.createdAt,
        'updatedAt': cart.updatedAt,
        'deleteAt': cart.deleteAt
    }
    return jsonify(cart_data), 200

@app.route('/order', methods=['POST'])
def create_order():
    data = request.get_json()
    cartId = data.get('cartId')
    userId = data.get('userId')

    if not cartId or not userId:
        return jsonify({'error': 'Missing required fields'}), 400

    new_order = Order(cartId=cartId, userId=userId)
    db.session.add(new_order)
    db.session.commit()

    return jsonify({'message': 'Order created successfully'}), 201

@app.route('/orderPayment/<int:id>', methods=['PUT'])
def payment_status(id):
    order = Order.query.get(id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    order.paymentStatus = 'paid'
    db.session.commit()

    return jsonify({'message': 'Payment status updated successfully'}), 200

@app.route('/orderDelivery/<int:id>',methods=['PUT'])
def deliver_status(id):
    order = Order.query.get(id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    order.status = 'delivered'
    db.session.commit()

    return jsonify({'message': 'Delivery status updated successfully'}), 200

@app.route('/getorderbyuser/<int:userId>', methods=['GET'])
def get_order(userId):
    orders = Order.query.filter_by(userId=userId).all()
    order_list = []
    for order in orders:
        order_data = {
            'id': order.id,
            'cartId': order.cartId,
            'userId': order.userId,
            'paymentStatus': order.paymentStatus,
            'deleteStatus': order.deleteStatus,
            'createdAt': order.createdAt,
            'updatedAt': order.updatedAt,
            'deleteAt': order.deleteAt
        }
        order_list.append(order_data)
    
    return jsonify(order_list), 200

if __name__ == '__main__':  
    app.run(debug=True)