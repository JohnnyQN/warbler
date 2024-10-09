import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, MessageForm, RegisterForm, UserEditForm
from models import db, connect_db, User, Message, Like

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///warbler')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)

# Only run `db.create_all()` outside of tests
if os.environ.get('FLASK_ENV') != 'production' and os.environ.get('FLASK_ENV') != 'testing':
    with app.app_context():
        db.create_all()


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""
    if CURR_USER_KEY in session:
        g.user = db.session.get(User, session[CURR_USER_KEY])
    else:
        g.user = None


def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/')
def homepage():
    if g.user:
        messages = Message.query.order_by(Message.timestamp.desc()).all()
        return render_template('home.html', messages=messages)
    return render_template('home-anon.html')


@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = UserAddForm()
    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()
        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)
        return redirect("/")

    return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")
        flash("Invalid credentials.", 'danger')
    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    do_logout()
    flash("Successfully logged out!", "success")
    return redirect('/')


@app.route('/users')
def list_users():
    search = request.args.get('q')
    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()
    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    user = User.query.get_or_404(user_id)
    messages = (Message.query.filter(Message.user_id == user_id)
                .order_by(Message.timestamp.desc())
                .limit(100).all())
    return render_template('users/show.html', user=user, messages=messages)


@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()
        return redirect(f"/users/{g.user.id}")

    return render_template('messages/new.html', form=form)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def messages_destroy(message_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    msg = Message.query.get(message_id)
    db.session.delete(msg)
    db.session.commit()
    return redirect(f"/users/{g.user.id}")


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""
    form = UserEditForm(obj=g.user)
    if form.validate_on_submit():
        g.user.username = form.username.data
        g.user.email = form.email.data
        db.session.commit()
        return redirect(f"/users/{g.user.id}")
    return render_template("users/edit.html", form=form)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    do_logout()
    db.session.delete(g.user)
    db.session.commit()
    return redirect("/signup")

@app.route('/users/<int:user_id>/followers')
def show_followers(user_id):
    user = User.query.get_or_404(user_id)
    followers = user.followers
    return render_template('users/followers.html', user=user, followers=followers)

@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    user = User.query.get_or_404(user_id)
    following = user.following
    return render_template('users/following.html', user=user, following=following)

