from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os
from cloudipsp import Api, Checkout

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quitars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)

log_user_name = 'not'
from_req = 'Guitars'
sort_pos = 'Цена (по возрастанию)'

#КЛАССЫ
class Guitar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    popularity = db.Column(db.Integer)
    photo = db.Column(db.Integer)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Гитара: {self.title}"


class Amp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    popularity = db.Column(db.Integer)
    photo = db.Column(db.Integer)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return True


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.Integer)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return True


class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.Integer)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return True


class Pedal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.Integer)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return True


class Cable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.Integer)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return True


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password1 = db.Column(db.String, nullable=False)
    password2 = db.Column(db.String, nullable=False)

    def __repr__(self):
        return True


with app.app_context():
    db.create_all()


class Dtbase:
    def __init__(self, db):
        self.db = db
        self.cur = db.cursor()


class Selectsetup:
    def __init__(self, budget):
        self.budget = budget
        self.guitars = Guitar.query.all()
        self.amps = Amp.query.all()
        self.prices()

    def prices(self):
        self.guitar_price_true = int(self.budget / 2)
        self.amp_price_true = int(self.budget / 3)

        guitar_result = Guitar.query.order_by(db.func.abs(Guitar.price - self.guitar_price_true)).first()
        amp_result = Amp.query.order_by(db.func.abs(Amp.price - self.amp_price_true)).first()

        self.guitar_id = guitar_result.id
        self.guitar_price = guitar_result.price

        self.amp_id = amp_result.id
        self.amp_price = amp_result.price

        if self.budget in range(150000, 249000):
            self.pedal_price = 10000
        elif self.budget >= 250000:
            self.pedal_price = 22000
        else:
            self.pedal_price = 0

        self.case_price = int(self.budget / 8)
        self.cabel_price = 3000
        self.belt_price = 6000

        self.total = (self.guitar_price + self.amp_price + self.pedal_price +
                      self.case_price + self.cabel_price + self.belt_price)

        self.error_g = self.total - self.budget

        if self.error_g in range(-10000, 10000):
            self.case_price = int(self.budget / 8)
        else:
            if self.error_g <= -10000:
                self.case_price = int(self.budget - self.total + 10000)

        self.total = (self.guitar_price + self.amp_price + self.pedal_price +
                      self.case_price + self.cabel_price + self.belt_price)

        return int(self.total)


class Addcart:
    def __init__(self, id, from_req):
        self.from_req = from_req
        self.id = id
        self.guitars = Guitar.query.all()
        self.amps = Amp.query.all()
        self.cart()

    def cart(self):
        if self.from_req == 'Guitars':
            guitar = Guitar.query.get(self.id)
            existing_pos = Cart.query.filter_by(id=guitar.id).first()
            if existing_pos:
                return 'Success'
            else:
                new_pos = Cart(id=guitar.id, title=guitar.title, photo=guitar.photo, price=guitar.price)
                db.session.add(new_pos)
                db.session.commit()
                return 'Success'
        elif self.from_req == 'Amplifiers':
            amp = Amp.query.get(self.id)
            existing_pos = Cart.query.filter_by(id=amp.id).first()
            if existing_pos:
                return 'Success'
            else:
                new_pos = Cart(id=amp.id, title=amp.title, photo=amp.photo, price=amp.price)
                db.session.add(new_pos)
                db.session.commit()
                return 'Success'


def main():
    app.run()

#СТРАНИЧКИ
@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    global log_user_name
    global from_req
    global sort_pos
    from_req = 'Guitars'

    if request.method == 'POST':
        sort_pos = request.form['sort_pos']
        selected_brand = request.form.get('brand')
        if sort_pos == 'Цена (по возрастанию)':
            guitars = Guitar.query.order_by(Guitar.price).all()
        if sort_pos == 'Цена (по убыванию)':
            guitars = Guitar.query.order_by(Guitar.price.desc()).all()
        if sort_pos == 'Популярность (по возрастанию)':
            guitars = Guitar.query.order_by(Guitar.popularity).all()
        if sort_pos == 'Популярность (по убыванию)':
            guitars = Guitar.query.order_by(Guitar.popularity.desc()).all()
        return render_template('index.html', guitars=guitars, log_user_name=log_user_name, from_req=from_req,
                               sort_pos=sort_pos)
    else:
        guitars = Guitar.query.order_by(Guitar.price).all()
        return render_template('index.html', guitars=guitars, log_user_name=log_user_name, from_req=from_req,
                               sort_pos=sort_pos)

@app.route('/amp', methods=['GET', 'POST'])
def amp():
    global log_user_name
    global from_req
    global sort_pos
    from_req = 'Amplifiers'

    if request.method == 'POST':
        sort_pos = request.form['sort_pos']
        if sort_pos == 'Цена (по возрастанию)':
            amps = Amp.query.order_by(Amp.price).all()
        if sort_pos == 'Цена (по убыванию)':
            amps = Amp.query.order_by(Amp.price.desc()).all()
        if sort_pos == 'Популярность (по возрастанию)':
            amps = Amp.query.order_by(Amp.popularity).all()
        if sort_pos == 'Популярность (по убыванию)':
            amps = Amp.query.order_by(Amp.popularity.desc()).all()
        return render_template('amp.html', amps=amps, log_user_name=log_user_name, from_req=from_req, sort_pos=sort_pos)
    else:
        amps = Amp.query.order_by(Amp.price).all()
        return render_template('amp.html', amps=amps, log_user_name=log_user_name, from_req=from_req, sort_pos=sort_pos)


@app.route('/about')
def about():
    return render_template('about.html', from_req=from_req, log_user_name=log_user_name)


@app.route('/case')
def case():
    global log_user_name
    global from_req
    cases = Case.query.order_by(Case.price).all()
    return render_template('case.html', cases=cases, log_user_name=log_user_name, from_req=from_req)


@app.route('/cable')
def cable():
    global log_user_name
    global from_req
    cables = Cable.query.order_by(Cable.price).all()
    return render_template('cable.html', cables=cables, log_user_name=log_user_name, from_req=from_req)


@app.route('/pedal')
def pedal():
    global log_user_name
    global from_req
    pedals = Pedal.query.order_by(Pedal.price).all()
    return render_template('pedal.html', pedals=pedals, log_user_name=log_user_name, from_req=from_req)


@app.route('/add', methods=['POST', 'GET'])
def add():
    global from_req
    if from_req == 'Guitars':
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            popularity = request.form['popularity']
            price = request.form['price']
            photo = request.form['photo']

            guitar = Guitar(title=title, description=description, price=price, photo=photo, popularity=popularity)

            try:
                db.session.add(guitar)
                db.session.commit()
                return redirect('/index')
            except:
                return "Err"
        else:
            return render_template('add.html', log_user_name=log_user_name, from_req=from_req)
    elif from_req == 'Amplifiers':
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            popularity = request.form['popularity']
            price = request.form['price']
            photo = request.form['photo']

            amp = Amp(title=title, description=description, price=price, photo=photo, popularity=popularity)

            try:
                db.session.add(amp)
                db.session.commit()
                return redirect('/amp')
            except:
                return "Err"
        else:
            return render_template('add.html', log_user_name=log_user_name, from_req=from_req)


@app.route('/guitar_page/<int:id>')
def show_guitar_page(id):
    if from_req == 'Guitars':
        guitars = Guitar.query.all()
        text_content = None
        for guitar in guitars:
            if guitar.id == id:
                text_file_name, _ = os.path.splitext(guitar.photo)
                text_file_path = os.path.join(app.static_folder, 'text', text_file_name + '.txt')
                if os.path.exists(text_file_path):
                    with open(text_file_path, 'r') as text_file:
                        text_content = text_file.read()
                return render_template('guitar_page.html', guitars=guitars, id=id, text_content=text_content, log_user_name=log_user_name, from_req=from_req)
        return render_template('guitar_page.html', guitars=guitars, id=id, log_user_name=log_user_name, from_req=from_req)


@app.route('/amp_page/<int:id>')
def show_amp_page(id):
    if from_req == 'Amplifiers':
        amps = Amp.query.all()
        text_content = None
        for amp in amps:
            if amp.id == id:
                text_file_name, _ = os.path.splitext(amp.photo)
                text_file_path = os.path.join(app.static_folder, 'text', text_file_name + '.txt')
                if os.path.exists(text_file_path):
                    with open(text_file_path, 'r') as text_file:
                        text_content = text_file.read()
                return render_template('amp_page.html', amps=amps, id=id, text_content=text_content, log_user_name=log_user_name, from_req=from_req)
        return render_template('amp_page.html', amps=amps, id=id, log_user_name=log_user_name, from_req=from_req)


@app.route('/setup', methods=['POST', 'GET'])
def setup():
    guitars = Guitar.query.all()
    amps = Amp.query.all()
    if request.method == 'POST':
        budget = int(request.form['budget'])
        setup_budget = Selectsetup(budget)
        return render_template('setup.html', from_req=from_req, log_user_name=log_user_name,
                               budget=budget, setup_budget=setup_budget, guitars=guitars, amps=amps)
    else:
        return render_template('setup.html', from_req=from_req, log_user_name=log_user_name,
                               budget=budget, setup_budget=setup_budget, guitars=guitars, amps=amps)


@app.route('/cart/<int:id>', methods=['GET', 'POST'])
def add_to_cart(id):
    global from_req
    guitars = Guitar.query.all()
    amps = Amp.query.all()
    if from_req == 'Guitars':
        add_cart = Addcart(id=id, from_req=from_req)
        res = add_cart.cart()
        return show_guitar_page(id)
    elif from_req == 'Amplifiers':
        add_cart = Addcart(id=id, from_req=from_req)
        res = add_cart.cart()
        return show_amp_page(id)



@app.route('/cart_page', methods=['GET', 'POST'])
def cart_page():
    global from_req
    guitars = Guitar.query.all()
    amps = Amp.query.all()
    cart_poss = Cart.query.all()
    total_price = db.session.query(db.func.sum(Cart.price)).scalar()
    return render_template('cart.html', from_req=from_req, log_user_name=log_user_name, cart_poss=cart_poss, total_price=total_price)


@app.route('/clear_cart', methods=['GET', 'POST'])
def clear_cart():
    Cart.query.delete()
    db.session.commit()
    return cart_page()


@app.route('/buy/<int:total_price>')
def buy(total_price):
    api = Api(merchant_id=1396424,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "USD",
        "amount": str(total_price) + '00'
    }
    url = checkout.url(data).get('checkout_url')

    return redirect(url)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    global log_user_name
    log_user_name = 'not'
    users = User.query.all()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password1 = request.form['password1']
        password2 = request.form['password2']

        users = User(name=name, email=email, password1=password1, password2=password2)

        if password1 == password2 and len(name) > 0:
            try:
                db.session.add(users)
                db.session.commit()
                return redirect('/login')
            except:
                flash('Введите данные')
                return redirect('/register')
        else:
            print("Err")
    else:
        return render_template('register.html', log_user_name=log_user_name, from_req=from_req)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global log_user_name
    log_user_name = 'not'
    users = User.query.all()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password1 = request.form['password1']

        user = User.query.filter_by(name=name, email=email, password1=password1).first()

        if user:
            if name == 'admin':
                log_user_name = 'admin'
            else:
                log_user_name = user.name
            return redirect('/index')
        else:
            flash('Данного имени пользователя не существует, вы не можете войти, но вы можете зарегистрироваться!')
            return redirect('/login')
    else:
        return render_template('login.html', users=users, log_user_name=log_user_name, from_req=from_req)


if __name__ == '__main__':
    main()