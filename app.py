from flask import Flask, render_template,url_for,request,flash,redirect,session, current_app
from application import RegistrationForm,LoginForm, Addproducts
from database import db, User, Brand, Category, Addproduct
from flask_uploads import IMAGES, UploadSet, configure_uploads , patch_request_class
import os
from flask_login import LoginManager



basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY']='asknankla'
app.config['UPLOADED_PHOTOS_DEST']= os.path.join(basedir,'static/images')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
photos = UploadSet('photos', IMAGES)
configure_uploads(app,photos)
patch_request_class(app) 




login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='customerLogin'
login_manager.needs_refresh_message_category='danger'
login_manager.login_message = u"Please login first"


def MagerDicts(dict1,dict2):
	if isinstance(dict1,list) and isinstance(dict2,list):
		return dict1+dict2
	elif isinstance(dict1,dict) and isinstance(dict2,dict):
		return dict(list(dict1.items())+list(dict2.items()))
	return False


@app.route('/', methods=['GET','POST'])
def home():
	page = request.args.get('page',1,type=int)
	brands = Brand.query.join(Addproduct,(Brand.id==Addproduct.brand_id)).all()
	products = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).paginate(page=page,per_page=8)
	categories = Category.query.join(Addproduct,(Category.id==Addproduct.category_id)).all()
	return render_template('ytindex.html', products=products,brands=brands,categories=categories)

@app.route('/product/<int:id>')
def single_page(id):
	product = Addproduct.query.get_or_404(id)
	brands = Brand.query.join(Addproduct,(Brand.id==Addproduct.brand_id)).all()
	categories = Category.query.join(Addproduct,(Category.id==Addproduct.category_id)).all()
	return render_template('single_page.html', product=product,categories=categories,brands=brands)




@app.route('/brand/<int:id>')
def get_brand(id):
	get_b = Brand.query.filter_by(id=id).first_or_404()
	page = request.args.get('page',1,type=int)
	brand = Addproduct.query.filter_by(brand=get_b).paginate(page=page,per_page=6)
	brands = Brand.query.join(Addproduct,(Brand.id==Addproduct.brand_id)).all()
	categories = Category.query.join(Addproduct,(Category.id==Addproduct.category_id)).all()

	return render_template('ytindex.html',brand=brand,brands=brands,categories=categories,get_b=get_b) 


@app.route('/categories/<int:id>')
def get_category(id):
	page = request.args.get('page',1,type=int)
	get_cat = Category.query.filter_by(id=id).first_or_404()
	get_cat_prod = Addproduct.query.filter_by(category=get_cat).paginate(page=page,per_page=6)
	categories = Category.query.join(Addproduct,(Category.id==Addproduct.category_id)).all()
	brands = Brand.query.join(Addproduct,(Brand.id==Addproduct.brand_id)).all()
	return render_template('ytindex.html', get_cat_prod=get_cat_prod,categories=categories,brands=brands,get_cat=get_cat)


@app.route('/admin', methods=['GET','POST'])
def admin():
	if 'email' not in session:
		flash(f'Plese Login First','danger')
		return redirect(url_for('login'))
	products = Addproduct.query.all()

	return render_template('index.html',products=products)


@app.route('/brands',methods=['GET','POST'])
def brands():
	if 'email' not in session:
		flash(f'Plese Login First','danger')
		return redirect(url_for('login'))
	brands = Brand.query.order_by(Brand.id.desc()).all()
	return render_template('brands.html',brands=brands)


@app.route('/category',methods=['GET','POST'])
def category():
	if 'email' not in session:
		flash(f'Plese Login First','danger')
		return redirect(url_for('login'))
	categories = Category.query.order_by(Category.id.desc()).all()
	return render_template('brands.html',categories=categories)

@app.route('/updatebrand/<id>', methods=['GET','POST'])
def updatebrand(id):
	if 'email' not in session:
		flash(f'Plese Login First','danger')
		return redirect(url_for('login'))
	updatebrand = Brand.query.get_or_404(id)
	brand = request.form.get('brand')
	if request.method =='	POST':
		updatebrand.name = brand
		flash(f'Your brand updated successfully','success')
		db.session.commit()
		return redirect(url_for('brands'))
	return render_template('updatebrand.html',updatebrand=updatebrand)


@app.route('/deletebrand/<int:id>', methods=["GET","POST"])
def deletebrand(id):
	brand = Brand.query.get(id)
	if request.method == 'POST':
		db.session.delete(brand)
		db.session.commit()
		flash(f'The brand {brand.name} is deleted from your database','success')
		return redirect(url_for('admin'))
	flash(f'The brand {brand.name} is  cant be deleted from your database','warning')
	return redirect(url_for('admin'))

@app.route('/updatecat/<id>', methods=['GET','POST'])
def updatecat(id):
	if 'email' not in session:
		flash(f'Plese Login First','danger')
		return redirect(url_for('login'))
	updatecat = Category.query.get_or_404(id)
	category = request.form.get('category')
	if request.method =='POST':
		updatecat.name = category
		flash(f'Your category updated successfully','success')
		db.session.commit()
		return redirect(url_for('category'))
	return render_template('updatebrand.html',updatecat=updatecat)




@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
    	data = User(name = form.name.data,username = form.username.data,email = form.email.data,password = form.password.data)
    	db.session.add(data)
    	db.session.commit()
    	flash(f'welcome {form.name.data} thankyou for registration','success')
    	return redirect(url_for('admin'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm(request.form)
	if request.method== 'POST':
		user = User.query.filter_by(email=form.email.data).first()
		if user and user.password==form.password.data:
			session['email'] = form.email.data
			flash(f'welcome {form.email.data} You are logged in','success')
		
			return redirect(url_for('admin'))
		else:

			flash(f'You entered wrong password','danger')
			
	return render_template('login.html',form=form)



@app.route('/addbrand',methods=['GET','POST'])
def addbrand():
	if request.method=='POST':
		getbrand=request.form['brand']
		brand=Brand(name=getbrand)
		db.session.add(brand)
		db.session.commit()
		flash(f'The Brand {getbrand} was added your database','success')
		return redirect(url_for('addbrand'))
	return render_template('addbrand.html',brands='brands')

@app.route('/addcat',methods=['GET','POST'])
def addcat():
	if request.method=='POST':
		getcat=request.form['category']
		cat=Category(name=getcat)
		db.session.add(cat)
		db.session.commit()
		flash(f'The category {getcat} was added to your database','success')
		return redirect(url_for('addcat'))
	return render_template('addbrand.html')


@app.route('/addproduct', methods=['GET','POST'])
def addproduct():
	brands = Brand.query.all()
	categories = Category.query.all()
	form=Addproducts(request.form)
	if request.method=='POST':
		name = form.name.data
		price = form.price.data
		discount = form.discount.data
		stock = form.stock.data
		colors = form.colors.data
		desc = form.desc.data
		brand = request.form['brand']
		category = request.form['category']
		image_1 = photos.save(request.files['image_1'])
		image_2 = photos.save(request.files['image_2'])
		image_3 = photos.save(request.files['image_3'])

		addpro = Addproduct(name=name, price=price, discount=discount, stock=stock, colors=colors,desc=desc,brand_id=brand,category_id=category,image_1=image_1,image_2=image_2,image_3=image_3)
		db.session.add(addpro)
		db.session.commit()
		flash(f'The product {name} is added to your database','success')
		return redirect('admin')

	return render_template('addproduct.html',form=form, brands=brands , categories=categories)



@app.route('/updateproduct/<int:id>', methods=['GET','POST'])
def updateproduct(id):
	brands = Brand.query.all()
	categories = Category.query.all()
	product = Addproduct.query.get_or_404(id)
	brand = request.form.get('brand')
	category = request.form.get('category')
	form = Addproducts(request.form)
	if request.method =='POST':

		product.name = form.name.data
		product.price = form.price.data
		product.colors = form.colors.data
		product.stock = form.stock.data
		product.discount = form.discount.data
		product.brand_id = brand
		product.category_id = category
		product.desc = form.desc.data
		if request.files.get('image_1'):
			try:
				os.unlike(os.path.join(current_app.root_path, "static/images/" + product.image_1))
				product.image_1 = photos.save(request.files['image_1'])
			except:
				product.image_1 = photos.save(request.files['image_1'])

		if request.files.get('image_2'):
			try:
				os.unlike(os.path.join(current_app.root_path, "static/images/" + product.image_1))
				product.image_1 = photos.save(request.files['image_2'])
			except:
				product.image_1 = photos.save(request.files['image_2'])


		if request.files.get('image_3'):
			try:
				os.unlike(os.path.join(current_app.root_path, "static/images/" + product.image_1))
				product.image_1 = photos.save(request.files['image_3'])
			except:
				product.image_1 = photos.save(request.files['image_3'])


		db.session.commit()
		flash(f'Your Product has been updated','success')
		return redirect(url_for('admin'))
	form.name.data = product.name
	form.price.data = product.price
	form.colors.data= product.colors
	form.desc.data=product.desc
	form.stock.data=product.stock
	form.discount.data=product.discount
	form.image_1.data = product.image_1



	return render_template('updateproduct.html',form=form, categories=categories, brands=brands, product=product)


@app.route('/addcart', methods=['GET','POST'])
def AddCart():
	try:
		product_id = request.form.get('product_id')
		quantity = request.form.get('quantity')
		colors = request.form.get('colors')
		product = Addproduct.query.filter_by(id = product_id).first()
		if product_id and quantity and colors and request.method=="POST":
			DictItems = {product_id:{'name':product.name,'price':product.price,'discount':product.discount,'color':colors,'quantity':quantity,'image':product.image_1,'colors':product.colors}}

			if 'Shoppingcart' in session:
				print(session['Shoppingcart'])
				if product_id in session['Shoppingcart']:
					print('This product is already added in your cart')
				else:
					session['Shoppingcart'] = MagerDicts(session['Shoppingcart'],DictItems)
					return redirect(request.referrer)
		
			else:

				session['Shoppingcart'] = DictItems
				return redirect(request.referrer)



	except Exception as e :
		print(e)
	
	finally:
		return redirect(request.referrer)


@app.route('/carts')
def getCart():

	brands = Brand.query.join(Addproduct,(Brand.id==Addproduct.brand_id)).all()
	categories = Category.query.join(Addproduct,(Category.id==Addproduct.category_id)).all()

	if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
		return redirect(url_for('home'))
	subtotal = 0
	grandtotal = 0 
	for key,product in session['Shoppingcart'].items():
		discount = (product['discount']/100) * float(product['price'])
		subtotal += float(product['price']) * int(product['quantity'])
		subtotal -=discount 
		tax = ('%.2f' % (.06* float(subtotal)))
		grandtotal = float("%.2f" % (1.06* subtotal))
	return render_template('carts.html',tax = tax, grandtotal=grandtotal,brands=brands,categories=categories)



@app.route('/updatecart/<int:code>',methods=['POST'])
def updatecart(code):
	if 'Shoppingcart' not in session and len(session['Shoppingcart']) <=0 :
		return redirect(url_for('home'))

	if request.method=='POST':
		quantity = request.form.get('quantity')
		color = request.form.get('color')
		try:
			session.modified = True
			for key , item in session['Shoppingcart'].items():
				if int(key)==code:
					item['quantity'] = quantity
					item['color'] = color
					flash('Item is updated','success')
					return redirect(url_for('getCart'))


		except Exception as e:
			print(e)
			return redirect(url_for('getCart'))



@app.route('/deleteitem/<int:id>')
def deleteitem(id):
	if 'Shoppingcart' not in session and len(session['Shoppingcart']) <=0:
		return redirect(url_for('home'))

	try:
		session.modified= True
		for key, item in session['Shoppingcart'].items():
			if int(key) == id:
				session['Shoppingcart'].pop(key,None)
				return redirect(url_for('getCart'))

	except Exception as e:
		print(e)
		return redirect(url_for('getCart'))


@app.route('/clearcart')
def clearcart():
	try:
		session.pop('Shoppingcart',None)
		return redirect(url_for('home'))
	except Exception as e:
		print(e)



###########################customer


if __name__ == '__main__':

	app.run(debug=True)
