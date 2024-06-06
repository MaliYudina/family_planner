import logging
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for, session
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from dotenv import load_dotenv
from datetime import datetime
from extensions import db
from database.tables_setup import create_tables
from config.config import Config, secret_key
from forms import GroceriesForm
from models import User, Groceries, Tasks, Message, UserChoice, Settings
from flask_migrate import Migrate
from google_auth_oauthlib.flow import Flow
from services.waste_calendar.afval import check_waste
from services.weather.buienradar_weather import get_buienradar_weather
from services.transport.get_stations_schedule import get_data
from mock_transport import mock_dict_transport
from functools import wraps

load_dotenv('./.flaskenv')

application = Flask(__name__)
app = application  # This is required for AWS deployment

app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_ECHO'] = True
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
logging.basicConfig(level=logging.DEBUG)

google_json = Config.GOOGLE_CREDENTIALS_PATH
flow = Flow.from_client_secrets_file(
    google_json,
    scopes=['https://www.googleapis.com/auth/calendar'],
    redirect_uri='http://localhost:5000/oauth2callback'
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def update_status(model):
    def decorator(func):
        @wraps(func)
        def wrapper(item_id, *args, **kwargs):
            item = model.query.get(item_id)
            if item:
                item.completed = not item.completed
                db.session.commit()
                return jsonify(success=True, item_id=item.id, completed=item.completed)
            return jsonify(success=False, error="Item not found"), 404

        return wrapper

    return decorator


@app.route('/')
def index():
    app.logger.debug("loading index")
    if current_user.is_authenticated:
        user_name = current_user.username
    else:
        return redirect(url_for('login'))

    today_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    groceries = Groceries.query.all()
    tasks = Tasks.query.all()
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

    return render_template('index.html', user_name=user_name, today_date=today_date, groceries=groceries, tasks=tasks,
                           form=form, real_time_seconds=real_time_seconds, waste=waste,
                           grouped_transport=grouped_transport,
                           weather=weather, choices_with_users=choices_with_users)


@app.route('/add_grocery', methods=['POST'])
def add_grocery():
    data = request.get_json()
    title = data.get('title')
    if title:
        new_grocery = Groceries(title=title, completed=False, user_id=current_user.id)
        db.session.add(new_grocery)
        db.session.commit()
        return jsonify(success=True,
                       item={'id': new_grocery.id, 'title': new_grocery.title, 'completed': new_grocery.completed})
    return jsonify(success=False, error="Title is required"), 400


@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.get_json()
    title = data.get('title')
    if title:
        new_task = Tasks(title=title, completed=False, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        return jsonify(success=True, item={'id': new_task.id, 'title': new_task.title, 'completed': new_task.completed})
    return jsonify(success=False, error="Title is required"), 400


@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    item_id = data.get('id')
    completed = data.get('completed')
    item_type = data.get('type')

    if item_type == 'grocery':
        item = Groceries.query.get(item_id)
    elif item_type == 'task':
        item = Tasks.query.get(item_id)
    else:
        return jsonify(success=False, error="Invalid item type"), 400

    if item:
        item.completed = completed
        item.date_updated = datetime.utcnow()
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False, error="Item not found"), 404


@app.route('/register', methods=['GET', 'POST'])
def register():
    logging.debug("Register function called with method: {}".format(request.method))
    if request.method == 'GET':
        logging.debug("Handling GET request for /register")
        return render_template('register.html')

    try:
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')

        if not username or not password:
            flash('Both username and password are required!', 'error')
            logging.error("Username or password not provided.")
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('User already exists!', 'error')
            logging.error("Attempt to register with an existing username: {}".format(username))
            return redirect(url_for('register'))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        logging.info("New user registered successfully: {}".format(username))
        return redirect(url_for('login'))
    except Exception as e:
        logging.exception("Failed to register user: {}".format(e))
        flash('An error occurred during registration.', 'error')
        return redirect(url_for('register'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
    else:
        username = request.form.get('username')
        password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        error_message = 'Invalid username or password'
        if request.is_json:
            return jsonify({'message': error_message}), 401
        else:
            flash(error_message)
            return redirect(url_for('login'))

    login_user(user)
    if request.is_json:
        return jsonify({'message': 'logged in successfully'}), 200
    else:
        return redirect(url_for('index'))


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    print(session)  # Debug statement to print session data
    if '_user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['_user_id']
    user = User.query.get(user_id)

    if not user:
        return redirect(url_for('login'))

    settings = Settings.query.filter_by(username=user.username).first()

    if request.method == 'POST':
        email = request.form['email']
        telegram_account = request.form['telegram_account']
        address = request.form['address']
        route_origin = request.form['origin']
        route_destination = request.form['destination']

        if not settings:
            settings = Settings(
                username=user.username,
                route_origin=route_origin,
                route_destination=route_destination,
                email=email,
                telegram_account=telegram_account,
                address=address,
                user_id=user.id  # Ensure user_id is set correctly
            )
        else:
            settings.route_origin = route_origin
            settings.route_destination = route_destination
            settings.email = email
            settings.telegram_account = telegram_account
            settings.address = address

        db.session.add(settings)
        db.session.commit()

        # Reload the settings object to get the updated values
        settings = Settings.query.filter_by(username=user.username).first()

    # Ensure the settings object contains default values for the template
    if settings is None:
        settings = {
            'username': user.username,
            'route_origin': '',
            'route_destination': '',
            'email': '',
            'telegram_account': '',
            'address': ''
        }
    else:
        settings = {
            'username': settings.username,
            'route_origin': settings.route_origin,
            'route_destination': settings.route_destination,
            'email': settings.email,
            'telegram_account': settings.telegram_account,
            'address': settings.address
        }

    return render_template('settings.html', settings=settings, user=user)


@app.route('/post-message', methods=['POST'])
def post_message():
    message_text = request.form['message']
    message = Message(text=message_text, user_id=current_user.id)
    db.session.add(message)
    db.session.commit()
    return 'Message sent', 200


@app.route('/messages', methods=['GET'])
def get_messages():
    app.logger.debug("fetching messages")
    messages = Message.query.all()
    return render_template('messages.html', messages=messages)


@app.route('/choose', methods=['POST'])
@login_required
def choose():
    data = request.get_json()
    choice = data.get('choice')
    if choice:
        user_choice = UserChoice.query.filter_by(user_id=current_user.id).first()
        if not user_choice:
            user_choice = UserChoice(choice=choice, user_id=current_user.id)
            db.session.add(user_choice)
        else:
            user_choice.choice = choice
        try:
            db.session.commit()
            return jsonify(success=True, choice=choice)
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Failed to save choice: {e}")
            return jsonify(success=False, error="Failed to save choice"), 500
    return jsonify(success=False, error="Invalid request"), 400


@app.route('/get_choice', methods=['GET'])
@login_required
def get_choice():
    user_choice = UserChoice.query.filter_by(user_id=current_user.id).first()
    if user_choice:
        return jsonify(success=True, choice=user_choice.choice)
    return jsonify(success=False, error="No choice found"), 404


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    with app.app_context():
        create_tables()
    application.run(debug=True)
