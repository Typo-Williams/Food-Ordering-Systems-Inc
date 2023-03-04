from flask import request, jsonify,render_template,redirect,flash,url_for
from app import app, db
from datetime import datetime
from models import Customer, Order, Food, OrderItem #importing customized class from models
from flask_login import (current_user, LoginManager,
                             login_user, logout_user,
                             login_required)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(email):
    #getting the customer/user infor by email address
    return Customer.query.filter_by(email=email).first()

@login_manager.unauthorized_handler
def unauthorized():
     return render_template("unauthorized.html")

#------AUTHENTICATION ROUTES----------------

#route to login into the application
#admin user will get all the settings control like adding food,customer,search
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=='POST':
        email = request.form['email']
        user_password = request.form['user_password']
        #find the user/customer
        user=Customer.query.filter_by(email=email,user_password=user_password).first()
        #email='admin@mariopizza.com'
        #user = Customer.query.get(user_email=email)
        if user:
            user.authenticated = True
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            return redirect(url_for("index"))
        else:
            flash('Login failed, please try again')
            return render_template("login.html")
    else:
        return render_template("login.html")

#route to logout from the application    
@app.route("/logout", methods=["GET"])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return render_template("home.html")

# Route to display the homepage
@app.route('/')
def index():
    # db.drop_all()
    # db.create_all()
    #return to the home page of the app
    return render_template('home.html',current_user=current_user)

# Route to display coming soon message page for most of the static pages
@app.route('/comingsoon')
def coming_soon():
    return render_template('coming_soon.html')

#------CUSTOMER ROUTES----------------
# Route to create a new customer

@app.route('/customer', methods=['POST','GET'])
@login_required
def create_customer():
    if request.method=='GET':# if get request, display a form to create customer
        #display a from to add new customer
        return render_template('new_customer.html')
    else: #if post request, insert a new customer record 
        #getting form posted data into variables
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        user_password = request.form['user_password']
        #creating a instance of a customer
        new_customer = Customer(name=name, email=email, phone=phone,user_password=user_password)
        #saving data to database
        db.session.add(new_customer)
        db.session.commit()
        #store a message which will be displayed in new customer form
        flash('New customer created successfully')
        #display the new customer form after inserting new record with success message
        return render_template('new_customer.html') 

# Route to get information about all customers with their orders
@app.route('/customers', methods=['GET'])
@login_required
def get_customers_with_orders():
    customers = Customer.query.filter_by(role=1) #get all customers records
    #return to customer page to list customer and their respective orders
    return render_template('customers.html', customers=customers)

# Route to get order history for a specific customer
@app.route('/customer/<int:id>/orders', methods=['GET'])
@login_required
def get_customer_orders(id):
    customer = Customer.query.get(id) #get customer by ID
    if not customer:
        return jsonify({'message': 'Customer not found'})
    orders = customer.orders #get all the order of this customer
    orders_data = [] #empty array to store order details
    order_items_data=[] #empty array to store order item details
    
    for order in orders:#loop through all order as a customer can have multiple orders
        order_items_data=[]
        order_data = {
            'id': order.id,
            'order_time': order.order_time,
            'order_amount': 0 #initialing order amount as 0 as default
        }
        
        orders_items=order.order_items
        total_amount=0 #variable to store the total amount of particular order
        for orders_item in orders_items:#loop through all order items as one order can have multiple items
            order_item ={
                'food_name':orders_item.food.name,
                'quantity':orders_item.quantity,
                'rate':orders_item.food.price,
                'total_price': orders_item.total_price        
            }
            total_amount=total_amount+orders_item.total_price
            order_items_data.append(order_item) # add this order item to list
        order_data['order_amount']=total_amount # adding actual order amount
        order_data['order_items']=order_items_data
        orders_data.append(order_data) #add this order to list
    #display particular customer orders details
    return render_template('customer_orders.html',customer=customer,orders=orders_data,order_items=order_items_data)

#------FOOD ROUTES----------------
# Route to create a new food item
@app.route('/food', methods=['POST','GET'])
@login_required
def create_food():
    if request.method=='GET':
        return render_template('new_food.html')
    else:
        name = request.form['name']
        price = request.form['price']
        category=request.form['category']
        new_food = Food(name=name, price=price,category=category)
        db.session.add(new_food)
        db.session.commit()
        flash('New food item added successfully')
        return render_template('new_food.html')
    
# Route to list all food items
@app.route('/foods', methods=['GET'])
def food_list():
    food_items = Food.query.all()
    entrees=Food.query.filter_by(category='entree')
    appetizers=Food.query.filter_by(category='appetizer')
    desserts=Food.query.filter_by(category='dessert')
    drinks=Food.query.filter_by(category='drink')
    return render_template('foods.html', food_items=food_items,entrees=entrees,appetizers=appetizers,desserts=desserts,drinks=drinks)

#------ORDER ROUTES----------------
# Route to create a new order
@app.route('/order', methods=['POST','GET'])
@login_required
def create_order():
    if request.method=='GET':
        customers = Customer.query.filter_by(role=1) # returns all the customer in customer table excepts admins
        foods = Food.query.all() #returns all the foods in food table
        #return to new order page with customer and food list
        return render_template('new_order.html', customers=customers, foods=foods)
    else:
        #getting customer id from posted form
        customer_id = request.form['customer_id']
        customer = Customer.query.get(customer_id)#getting customer by ID
        if not customer: #if not a valid customer, return without placing an order
            return jsonify({'message': 'Customer not found'})
        # Create a new order
        new_order = Order(customer=customer,order_time=datetime.now())
        db.session.add(new_order)

        # Get the selected food items and their quantities from the form data
        food_items = request.form.getlist('food_items')
        for food_id in food_items:
            food = Food.query.filter_by(id=food_id).first()
            if food is not None: #if valid food
                quantity = int(request.form.get('quantity_{}'.format(food_id))) #get quantity by breaking the value after quantity_
                order_item = OrderItem(food=food, quantity=quantity,total_price=round(food.price*quantity,2),order=new_order)
                db.session.add(order_item)
        #commit the changes to the database
        db.session.commit()
        return redirect(url_for('get_order_details', id=new_order.id))
        

# Route to display the new order form page
@app.route('/order/new')
@login_required
def new_order():
    customers = Customer.query.filter_by(role=1) # returns all the customer in customer table
    foods = Food.query.all() #returns all the foods in food table
    #return to new order page with customer and food list
    return render_template('new_order.html', customers=customers, foods=foods)

# Route to display the particular order details
@app.route('/order/<int:id>', methods=['GET'])
@login_required
def get_order_details(id):
    
    order_details=[]
    # get the order details
    order = Order.query.get(id)
    # get the order items for the order from the database
    order_items = OrderItem.query.filter_by(order_id=id).all()
    order_details={
        'order1':order,
        'order_items':order_items
    }
    order_total= OrderItem.query.with_entities(db.func.sum(OrderItem.total_price).label("Grand_total")).filter(
        OrderItem.order_id == id).first()
    return render_template('order_details.html', order_details=order_details,order_total=order_total.Grand_total)

# Route to display the order history
@app.route('/orderhistory')
@login_required
def order_history():
     return redirect(url_for('get_customer_orders', id=current_user.id))
    
# Route to search form page
@app.route('/search')
@login_required
def search():
    #stores the search value
    search_query = request.args.get('search_query')
    #stores the search type i.e customer or order
    search_type = request.args.get('search_type')
    search_results = []
    #Get the result based on user type in value and search type
    if search_query and search_type:
        if search_type == 'customer': #if this search is to search customer
            #search the user type in value in customer table
            search_results = db.session.query(Customer).filter(Customer.name.ilike(f'%{search_query}%')).all()
        elif search_type == 'order': #if this search is to search order
            search_results=[]
            # get the order with the specified ID from the database
            order = Order.query.get(int(search_query))
            # get the order items for the order from the database
            order_items = OrderItem.query.filter_by(order_id=search_query).all()
            search_results={
                'order1':order,
                'order_items':order_items
            }
    #return to search page with the search result
    return render_template('search.html', search_query=search_query, search_type=search_type, search_results=search_results)

#application setup route
@app.route('/appsetup')
def app_setup():
    db.drop_all()
    db.create_all()
    #creating the admin user for the app
    new_customer = Customer(name='Super Admin', email='admin@email.com', phone='1212121212',user_password='admin@123',role=2)
    #saving data to database
    db.session.add(new_customer)
    new_customer = Customer(name='Test User', email='user@email.com', phone='1212121212',user_password='user',role=1)
    db.session.add(new_customer)
    db.session.commit()
    return render_template('home.html')
  