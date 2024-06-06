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

    family_members = db.relationship('FamilyMember', backref='parent_user', lazy=True)
    choices = db.relationship('UserChoice', backref='user', lazy=True)
    groceries = db.relationship('Groceries', backref='user', lazy=True)
    tasks = db.relationship('Tasks', backref='user', lazy=True)
    messages = db.relationship('Message', backref='user', lazy=True)
    settings = db.relationship('Settings', backref='user_settings', lazy=True, foreign_keys='Settings.user_id')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

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


@dataclass
class FamilyMember(db.Model):
    id: int
    name: str
    user_id: int

    __tablename__ = 'family_member'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<FamilyMember {self.name}>'


class UserChoice(db.Model):
    id: int = field(default=None)
    choice: str = field(default=None)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: int = field(default=None)

    __tablename__ = 'user_choice'
    id = db.Column(db.Integer, primary_key=True)
    choice = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<UserChoice {self.choice}>'


@dataclass
class Groceries(db.Model):
    id: int
    title: str
    date: datetime
    completed: bool
    user_id: int

    __tablename__ = 'groceries'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(140))
    date = db.Column(db.DateTime(), default=datetime.now())
    completed = db.Column(db.Boolean(), default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Groceries id: {self.id} - {self.title}>'


@dataclass
class Tasks(db.Model):
    id: int
    title: str
    date: datetime
    completed: bool
    user_id: int

    __tablename__ = 'tasks'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(140))
    date = db.Column(db.DateTime(), default=datetime.now())
    completed = db.Column(db.Boolean(), default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Tasks id: {self.id} - {self.title}>'


@dataclass
class Message(db.Model):
    id: int
    text: str
    timestamp: datetime
    user_id: int

    __tablename__ = 'message'
    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime(), default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Message id: {self.id} - {self.text}>'


@dataclass
class Settings(db.Model):
    id: int
    username: str
    route_origin: str
    route_destination: str
    email: str
    telegram_account: str
    address: str
    user_id: int

    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    route_origin = db.Column(db.String(128), nullable=False)
    route_destination = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    telegram_account = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('user_settings', lazy=True), foreign_keys=[user_id])

    def __repr__(self):
        return f'<Settings {self.username} - {self.route_origin} to {self.route_destination}>'
