from dataclasses import dataclass
from datetime import datetime
from app_front_flask.app import db

@dataclass
class Task(db.Model):
    id: int
    title: str
    date: datetime
    completed: bool
    __tablename__ = 'task'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(140))
    date = db.Column(db.DateTime(), default=datetime.now())
    completed = db.Column(db.Boolean(), default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Task id: {self.id} - {self.title}'


@dataclass
class Message(db.Model):
    id: int
    text: str
    timestamp: datetime

    __tablename__ = 'message'
    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime(), default=datetime.now)

    def __repr__(self):
        return f'<Message id: {self.id} - {self.text}>'
