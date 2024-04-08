import logging
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
from app_front_flask.models import User, Groceries, Message, UserChoice
from flask_migrate import Migrate
from flask_login import login_required, current_user
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow

load_dotenv('./.flaskenv')

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_ECHO'] = True
google_json = Config.GOOGLE_CREDENTIALS_PATH

flow = Flow.from_client_secrets_file(
    google_json,
    scopes=['https://www.googleapis.com/auth/calendar'],
    redirect_uri='http://localhost:5000/oauth2callback'
)

login_manager = LoginManager()
login_manager.init_app(app)

app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
logging.basicConfig(level=logging.DEBUG)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    app.logger.debug("loading index")
    # Check if a user is authenticated
    if current_user.is_authenticated:
        user_name = current_user.username
    else:
        user_name = 'Guest'  # Handle the non-authenticated case
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
    choices_with_users = db.session.query(UserChoice.choice, User.username) \
        .join(User, UserChoice.user_id == User.id) \
        .order_by(UserChoice.timestamp.desc()).all()
    print(choices_with_users)

    return render_template('index.html', user_name=user_name,
                           today_date=today_date, groceries=groceries, form=form,
                           real_time_seconds=real_time_seconds, waste=waste,
                           grouped_transport=grouped_transport, weather=weather,
                           choices_with_users=choices_with_users)





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


from flask import jsonify


@app.route('/create', methods=['POST'])
def create_task():
    print("Create route hit")  # Confirm this route is accessed
    form = GroceriesForm()
    if form.validate_on_submit():
        new_product = Groceries(title=form.title.data)
        db.session.add(new_product)
        db.session.commit()
        print(f"Product added: {new_product.title}")  # Log the added product
        return jsonify(success=True, product={'id': new_product.id,
                                              'title': new_product.title,
                                              'completed': new_product.completed})
    else:
        print("Form validation failed")
        return jsonify(success=False), 400


@app.route('/update/<int:product_id>', methods=['POST'])
def update_product(product_id):
    product = Groceries.query.get_or_404(product_id)
    product.completed = not product.completed
    db.session.commit()
    # Return the updated completed status to ensure frontend consistency
    return jsonify(success=True, completed=product.completed)



@app.route('/post-message', methods=['POST'])
def post_message():
    message_text = request.form['message']
    message = Message(text=message_text)
    print('the messages', message)
    db.session.add(message)
    db.session.commit()
    return 'Message sent', 200


@app.route('/messages', methods=['GET'])
def get_messages():
    app.logger.debug("fetching messages")
    messages = Message.query.all()
    print('Messages: ', messages)
    return render_template('messages.html', messages=messages)
from flask import request, redirect, url_for, render_template


@app.route('/choice_submitted/<choice>')
def choice_submitted(choice):
    return render_template('choice_submitted.html', choice=choice)


@app.route('/choose', methods=['POST', 'GET'])
@login_required
def choose():
    if request.is_json:
        data = request.json
        choice = data.get('choice')
        if choice:
            user_choice = UserChoice(choice=choice, user_id=current_user.id)
            try:
                db.session.add(user_choice)
                db.session.commit()
                return jsonify({'success': True, 'choice': choice})
            except Exception as e:
                db.session.rollback()  # Rollback in case of error
                app.logger.error(f"Failed to save choice: {e}")  # Log the error
                return jsonify({'success': False, 'error': 'Failed to save choice'}), 500
    return jsonify({'success': False, 'error': 'Invalid request'}), 400



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True)
