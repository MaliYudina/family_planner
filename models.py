from dataclasses import dataclass, field
from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


@dataclass
class User(db.Model):
    id: int
    username: str
    password_hash: str
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True  # You can add logic to check if the user's account is active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return str(self.id)  # Assuming 'id' is the primary key
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class UserChoice(db.Model):
    id: int = field(default=None)
    choice: str = field(default=None)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: int = field(default=None)  # Add this line

    __tablename__ = 'user_choice'
    id = db.Column(db.Integer, primary_key=True)
    choice = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Establish foreign key relationship

    # Define relationship to User
    user = db.relationship('User', backref=db.backref('choices', lazy=True))

    def __repr__(self):
        return f'<UserChoice {self.choice}>'


@dataclass
class Groceries(db.Model):
    id: int
    title: str
    date: datetime
    completed: bool
    __tablename__ = 'groceries'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(140))
    date = db.Column(db.DateTime(), default=datetime.now())
    completed = db.Column(db.Boolean(), default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Groceries id: {self.id} - {self.title}'


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
