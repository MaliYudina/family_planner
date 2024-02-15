from flask import Flask
from flask import jsonify
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user
from flask_login import LoginManager

from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

from app_front_flask.extensions import db
from app_front_flask.config import Config, secret_key
from app_front_flask.forms import GroceriesForm

from datetime import datetime
from mock_transport import mock_dict_transport
from waste_calendar.afval import check_waste
from transport.get_stations_schedule import get_data
from weather.buienradar_weather import get_buienradar_weather
from app_front_flask.models import User, Groceries, Message

load_dotenv('./.flaskenv')

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
login_manager = LoginManager()
login_manager.init_app(app)

app.config.from_object(Config)
db.init_app(app)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def index():
    # Check if a user is authenticated
    if current_user.is_authenticated:
        user_name = current_user.username
    else:
        # Redirect to the login page if no user is logged in
        return redirect(url_for('login'))
    today_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    groceries = Groceries.query.all()
    real_time_seconds = datetime.now().second
    if request.headers.get('X-Requested-With') == "XMLHttpRequest":
        return jsonify(groceries)
    waste = check_waste()
    # grouped_transport = get_data()
    grouped_transport = mock_dict_transport
    weather = get_buienradar_weather()

    form = GroceriesForm()

    return render_template('index.html', user_name=user_name,
                           today_date=today_date, groceries=groceries, form=form,
                           real_time_seconds=real_time_seconds, waste=waste,
                           grouped_transport=grouped_transport, weather=weather)






@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username is None or password is None:
        return jsonify({'message': 'missing arguments'}), 400

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'message': 'user already exists'}), 400

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'user registered', 'username': user.username}), 201


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Serve the login form on GET requests
    if request.method == 'GET':
        return render_template('login.html')

    # Below logic handles POST requests
    if request.is_json:
        # For JSON-based requests
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
    else:
        # For form submissions
        username = request.form.get('username')
        password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        error_message = 'Invalid username or password'
        if request.is_json:
            return jsonify({'message': error_message}), 401
        else:
            flash(error_message)
            return redirect(url_for('login'))  # Redirects back to login to display the error

    login_user(user)
    if request.is_json:
        return jsonify({'message': 'logged in successfully'}), 200
    else:
        return redirect(url_for('index'))  # Redirect to the main page after login



@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/create', methods=['POST'])
def create_task():
    form = GroceriesForm(request.form)
    if form.validate_on_submit():
        new_product = Groceries(title=form.title.data)
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!')
    else:
        flash('Error adding product.')
    return redirect(url_for('index'))


@app.route('/post-message', methods=['POST'])
def post_message():
    message_text = request.form['message']
    message = Message(text=message_text)
    print('the messages', message)
    db.session.add(message)
    db.session.commit()
    return 'Message received', 200


@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.all()
    print('Messages: ', messages)
    return render_template('messages.html', messages=messages)


if __name__ == '__main__':
    app.run()
