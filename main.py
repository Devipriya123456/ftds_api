from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:root@localhost/cartorders'
db=SQLAlchemy(app)
class Cart(db.Model):
    id=db.Column(db.Integer,autoincrement=True,primary_key=True)
    service_id=db.Column(db.Integer)
    quantity=db.Column(db.Integer)
    user_id=db.Column(db.Integer)
    delete_status=db.Column(db.Boolean,default=False)
    status=db.Column(db.String(50),default='Incart')
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    updated_at=db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    deleted_at=db.Column(db.DateTime,nullable=True)
    def to_dict(self):
        return {'id':self.id,
                'service_id':self.service_id,
                'quantity':self.quantity,
                'user_id':self.user_id,
                'delete_status':self.delete_status,
                'status':self.status,
                'created_at':self.created_at,
                'updated_at':self.updated_at,
                'deleted_at':self.deleted_at}

@app.route('/cart',methods=['GET'])
def home():
    cart=Cart.query.filter(Cart.delete_status!=True).all()
    return jsonify([c.to_dict() for c in cart])


@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart_by_user(user_id):
    carts = Cart.query.filter_by(user_id=user_id, delete_status=False).all()
    return jsonify([c.to_dict() for c in carts])

@app.route('/addcart',methods=['POST'])
def create_cart():
    data=request.json
    addProduct=Cart(service_id=data["service_id"],quantity=data['quantity'],user_id=data['user_id'],status=data['status'])
    db.session.add(addProduct)
    db.session.commit()
    return "success"

@app.route('/updatecart/<int:user_id>',methods=['PUT'])
def update_cart(user_id):
    data=request.json
    carts=Cart.query.filter_by(user_id=user_id).all()
    for c in carts:
        c.service_id=data.get('service_id',c.service_id)
        c.user_id=data.get('user_id',c.user_id)
        c.quantity=data.get('quantity',c.quantity)
        c.status = data.get('status', c.status)
        c.updated_at = datetime.utcnow()

    db.session.commit()
    return "success"

@app.route('/increasequantity/<int:id>',methods=['PUT'])
def increase_quantity(id):
    cart=Cart.query.get(id)
    if not cart:
        return 'Invalid id'
    cart.quantity +=1
    cart.updated_at= datetime.utcnow()
    db.session.commit()
    return "increased"

@app.route('/decreasequantity/<int:id>',methods=['PUT'])
def decrease_quantity(id):
    cart=Cart.query.get(id)
    if not cart:
        return 'Invalid id'
    cart.quantity -=1
    cart.updated_at= datetime.utcnow()
    db.session.commit()
    return "decreased"

@app.route('/delete/<int:id>',methods=['PUT'])
def delete_cart(id):
    cart=Cart.query.get(id)
    if not cart:
        return 'Invalid id'
    cart.delete_status=True
    cart.deletd_at=datetime.utcnow()
    db.session.commit()
    return "Deleted successfully"

if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run()