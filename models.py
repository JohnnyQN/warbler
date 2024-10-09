from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class Follows(db.Model):
    """Connection of a follower <-> followed_user."""
    __tablename__ = 'follows'
    user_being_followed_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), primary_key=True)
    user_following_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), primary_key=True)

class Like(db.Model):
    """Mapping user likes to messages."""
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id', ondelete='cascade'), nullable=False)

class User(db.Model):
    """User model."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    image_url = db.Column(db.Text, default="/static/images/default-pic.png")
    header_image_url = db.Column(db.Text, default="/static/images/warbler-hero.jpg")
    bio = db.Column(db.Text)
    location = db.Column(db.Text)
    password = db.Column(db.Text, nullable=False)

    messages = db.relationship('Message', backref="user")
    followers = db.relationship(
        "User", 
        secondary="follows", 
        primaryjoin=(Follows.user_being_followed_id == id), 
        secondaryjoin=(Follows.user_following_id == id),
        overlaps="following"
    )
    following = db.relationship(
        "User", 
        secondary="follows", 
        primaryjoin=(Follows.user_following_id == id), 
        secondaryjoin=(Follows.user_being_followed_id == id),
        overlaps="followers"
    )
    likes = db.relationship('Message', secondary="likes")

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user."""
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        user = cls(username=username, email=email, password=hashed_pwd, image_url=image_url)
        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Authenticate user."""
        user = cls.query.filter_by(username=username).first()
        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        return False

class Message(db.Model):
    """An individual message ("warble")."""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(140), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

def connect_db(app):
    """Connect this database to provided Flask app."""
    db.app = app
    db.init_app(app)
