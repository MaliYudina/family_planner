from flask import Flask
from flask import jsonify
from flask import render_template
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, url_for
from app_front_flask.config import Config
from app_front_flask.forms import TaskForm
from datetime import datetime
from mock_transport import mock_dict_transport

from waste_calendar.afval import check_waste
from transport.get_stations_schedule import get_data
from weather.buienradar_weather import get_buienradar_weather

load_dotenv('./.flaskenv')

app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)
from app_front_flask.models import Task, Message


@app.route('/')
def index():
    user_name = "Jack Smith!"
    today_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tasks = Task.query.all()
    real_time_seconds = datetime.now().second
    if request.headers.get('X-Requested-With') == "XMLHttpRequest":
        return jsonify(tasks)
    # return render_template('index.html', name=name)
    waste = check_waste()
    grouped_transport = get_data()
    # grouped_transport = mock_dict_transport
    weather = get_buienradar_weather()

    form = TaskForm()

    return render_template('index.html', user_name=user_name,
                           today_date=today_date, tasks=tasks, form=form,
                           real_time_seconds=real_time_seconds, waste=waste,
                           grouped_transport=grouped_transport, weather=weather)



@app.route('/create', methods=['POST'])
def create_task():
    user_input = request.get_json()
    form = TaskForm(data=user_input)
    if form.validate():
        task = Task(title=form.title.data)
        db.session.add(task)
        db.session.commit()

        return jsonify(task)
    return redirect(url_for('index'))

@app.route('/settings')
def settings():
    return render_template('settings.html')



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


# @app.route('/', methods=['GET'])


if __name__ == '__main__':
    app.run()
