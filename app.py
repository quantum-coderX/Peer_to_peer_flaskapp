from flask import Flask, render_template, url_for, request, jsonify, flash, redirect
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String, Float
from forms import LoginForm, RegistrationForm
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import numpy as np
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here' 

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'peer_to_peer.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)

# Initialize login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    bio = db.Column(db.Text, nullable=True)
    avatar = db.Column(db.String(200), nullable=True, default='default.jpg')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

# Define Skill model
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Skill {self.name}>'

# Define UserSkill model
class UserSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    skill_level = db.Column(db.Integer, nullable=False)  # 1-5 rating
    is_teacher = db.Column(db.Boolean, default=False)  # True if user can teach, False if wants to learn
    
    # Define relationships
    user = db.relationship('User', backref=db.backref('skills', lazy=True))
    skill = db.relationship('Skill', backref=db.backref('users', lazy=True))
    
    def __repr__(self):
        role = "Teacher" if self.is_teacher else "Learner"
        return f'<UserSkill {self.user.username} - {self.skill.name} ({role})>'

# Define Connection model
class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    learner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define relationships
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref=db.backref('teaching_connections', lazy=True))
    learner = db.relationship('User', foreign_keys=[learner_id], backref=db.backref('learning_connections', lazy=True))
    skill = db.relationship('Skill', backref=db.backref('connections', lazy=True))
    
    def __repr__(self):
        return f'<Connection {self.teacher.username} teaching {self.learner.username} - {self.skill.name}>'

# Define Resource model
class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(200), nullable=True)
    file_path = db.Column(db.String(200), nullable=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define relationships
    skill = db.relationship('Skill', backref=db.backref('resources', lazy=True))
    user = db.relationship('User', backref=db.backref('shared_resources', lazy=True))
    
    def __repr__(self):
        return f'<Resource {self.title} for {self.skill.name}>'

@app.route('/')
def index():
    return render_template("Index.html")

@app.route('/services')
def services():
    return render_template("services.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    form = LoginForm()
    if form.validate_on_submit():
        # Find the user by email
        user = User.query.filter_by(email=form.email.data).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
            
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()
        
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
        elif existing_email:
            flash('Email already registered. Please use a different email.', 'danger')
        else:
            # Create a new user
            new_user = User(username=form.username.data, email=form.email.data)
            new_user.set_password(form.password.data)
            
            # Add to the database
            db.session.add(new_user)
            db.session.commit()
            
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
            
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's teaching skills
    teaching_skills = UserSkill.query.filter_by(user_id=current_user.id, is_teacher=True).all()
    
    # Get user's learning skills
    learning_skills = UserSkill.query.filter_by(user_id=current_user.id, is_teacher=False).all()
    
    # Get user's teaching connections
    teaching_connections = Connection.query.filter_by(teacher_id=current_user.id).all()
    
    # Get user's learning connections
    learning_connections = Connection.query.filter_by(learner_id=current_user.id).all()
    
    # Get resources relevant to user's skills
    user_skill_ids = [skill.skill_id for skill in teaching_skills + learning_skills]
    resources = Resource.query.filter(Resource.skill_id.in_(user_skill_ids)).all() if user_skill_ids else []
    
    return render_template('dashboard.html', 
                          teaching_skills=teaching_skills,
                          learning_skills=learning_skills,
                          teaching_connections=teaching_connections,
                          learning_connections=learning_connections,
                          resources=resources)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)
