from flask import Flask, render_template, url_for, request, jsonify, flash, redirect
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
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

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

@app.route('/')
def index():
    return render_template("Index.html")

@app.route('/services')
def services():
    return render_template("services.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Find the user by email
        user = User.query.filter_by(email=form.email.data).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(form.password.data):
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)
