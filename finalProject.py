from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# Connect to database
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)


# Fake Restaurants
# restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}

# restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]


# Fake Menu Items
# items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
# item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}
# items = []


@app.route('/')
@app.route('/restaurants')
def showRestaurants():
    print 'connecting to database...'
    session = DBSession()
    print 'database connected. Retrieving restaurants...'
    restaurants = session.query(Restaurant).all()
    restaurantCounts = len(restaurants)
    print str(restaurantCounts)+' restaurants retrieved. Rendering template...'
    return render_template('restaurants.html', restaurants=restaurants, length=restaurantCounts)

@app.route('/restaurant/new', methods=['GET','POST'])
def newRestaurant():

    if request.method == 'GET':
        return render_template('newRestaurant.html')
    # on a POST request
    else:
        session = DBSession()
        newRestaurant = Restaurant(name=request.form['name'])
        session.add(newRestaurant)
        session.commit()
        flash('New Restaurant created!!')
        return redirect(url_for('showRestaurants'))

@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET','POST'])
def editRestaurant(restaurant_id):
    session = DBSession()
    restaurant_edit = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'GET':
        return render_template('editRestaurant.html',restaurant=restaurant_edit)
    else:  # POST
        restaurant_edit.name = request.form['name']
        session.add(restaurant_edit)
        session.commit()
        flash('Restaurant succesfully edited!!')
        return redirect(url_for('showRestaurants'))

@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
    if request.method == 'GET':
        return render_template('deleteRestaurant.html',restaurant_id=restaurant_id)
    else:  #POST
        session = DBSession()
        restaurant_delete = session.query(Restaurant).filter_by(id=restaurant_id).one()
        session.delete(restaurant_delete)
        session.commit()
        flash('Restaurant succesfully deleted!!')
        return redirect(url_for('showRestaurants'))

@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    session = DBSession()
    restaurant_name = session.query(Restaurant).filter_by(id=restaurant_id).one().name
    menuItems = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    countItems = len(menuItems)
    return render_template('menu.html',restaurant_id=restaurant_id, restaurant_name=restaurant_name,
                            menus=menuItems, length=countItems)

@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    if request.method == 'GET':
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)
    else:  # POST
        session = DBSession()
        newMenu = MenuItem(name=request.form['name'], price=request.form['price'],
                           description=request.form['description'],course=request.form['course'],
                           restaurant_id=restaurant_id)
        session.add(newMenu)
        session.commit()
        flash('New Menu Item created!!')
        return redirect(url_for('showMenu',restaurant_id=restaurant_id))

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    session = DBSession()
    targetMenu = session.query(MenuItem).filter_by(id=menu_id).one()

    if request.method == 'GET':
        return render_template('editmenuitem.html', restaurant_id=restaurant_id, menu=targetMenu)
    else:  #POST
        if (request.form['name'] != ''):
            targetMenu.name = request.form['name']
        if (request.form['description'] != ''):
            targetMenu.description = request.form['description']
        if (request.form['price'] != ''):
            targetMenu.price = request.form['price']
        if (request.form['course'] != ''):
            targetMenu.course = request.form['course']
        session.add(targetMenu)
        session.commit()
        flash('Menu Item succesfully edited!!')
        return redirect(url_for('showMenu',restaurant_id=restaurant_id))

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    if request.method == 'GET':
        return render_template('deletemenuitem.html',restaurant_id=restaurant_id, menu_id=menu_id)
    else:  #POST
        session = DBSession()
        menu_delete = session.query(MenuItem).filter_by(id=menu_id).one()
        session.delete(menu_delete)
        session.commit()
        flash('Menu Item succesfully deleted!!')
        return redirect(url_for('showMenu',restaurant_id=restaurant_id))

# These are for API calls that returns JSON file
@app.route('/restaurants/JSON')
def restaurantsJSON():
    session = DBSession()
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants=[r.serialize for r in restaurants])

@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenusJSON(restaurant_id):
    session = DBSession()
    menus = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(Menus=[menu.serialize for menu in menus])


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurantMenuItemJSON(restaurant_id, menu_id):
    session = DBSession()
    menu = session.query(MenuItem).filter_by(restaurant_id=restaurant_id,id=menu_id).one()
    return jsonify([menu.serialize])

if __name__ == '__main__':
    app.secret_key = "super secret key"
    app.debug = True  #rerun the code when it detects code change
    app.run(host = '0.0.0.0', port = 5000)