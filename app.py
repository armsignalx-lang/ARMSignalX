import os
from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secure-key-777'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/artx123453/trading_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Մոդելներ
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    full_name = db.Column(db.String(100), default="Նշված չէ")
    email = db.Column(db.String(100), default="Նշված չէ")
    phone = db.Column(db.String(20), default="Նշված չէ")
    is_approved = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(80))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Լեզուների ֆունկցիաներ ---
@app.context_processor
def inject_globals():
    return {
        'lang': session.get('lang', 'hy'),
        'now': datetime.utcnow()
    }

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in ['hy', 'ru', 'en']:
        session['lang'] = lang
        session.modified = True
    return redirect(request.referrer or url_for('index'))

# --- Հիմնական Route-ներ ---
@app.route('/')
@login_required
def index():
    if not current_user.is_approved and current_user.username != 'admin':
        return "<h1>Ձեր հաշիվը հաստատված չէ:</h1><a href='/logout'>Ելք</a>"
    messages = Message.query.order_by(Message.timestamp.desc()).limit(30).all()
    messages.reverse()
    return render_template('index.html', user=current_user.username, messages=messages)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username'), password=request.form.get('password')).first()
        if user:
            user.last_seen = datetime.utcnow()
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        u_name = request.form.get('username')
        is_admin = (User.query.count() == 0)
        new_user = User(
            username='admin' if is_admin else u_name,
            password=request.form.get('password'),
            is_approved=is_admin
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Ադմինիստրատորի Route-ներ ---
@app.route('/admin_panel')
@login_required
def admin_panel():
    if current_user.username != 'admin':
        return redirect(url_for('index'))
    users = User.query.filter(User.username != 'admin').all()
    return render_template('admin.html', users=users)

@app.route('/approve_user/<int:user_id>', methods=['POST'])
@login_required
def approve_user(user_id):
    if current_user.username == 'admin':
        user = User.query.get_or_404(user_id)
        user.is_approved = True
        db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/kick_user/<int:user_id>', methods=['POST'])
@login_required
def kick_user(user_id):
    if current_user.username == 'admin':
        user = User.query.get_or_404(user_id)
        user.is_approved = False
        db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/reject_user/<int:user_id>', methods=['POST'])
@login_required
def reject_user(user_id):
    if current_user.username == 'admin':
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/update_announcement', methods=['POST'])
@login_required
def update_announcement():
    if current_user.username == 'admin':
        text = request.form.get('announcement_text')
        if text:
            new_msg = Message(sender="SYSTEM", content=text)
            db.session.add(new_msg)
            db.session.commit()
    return redirect(url_for('admin_panel'))

with app.app_context():
    db.create_all()

application = app
