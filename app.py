import os
from datetime import datetime

from flask import Flask, render_template, url_for, request, jsonify, flash, redirect
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String, Float
from werkzeug.security import generate_password_hash, check_password_hash

from forms import LoginForm, RegistrationForm, SkillForm, UserSkillForm, ResourceForm, ConnectionRequestForm, ProfileUpdateForm, PostForm, DeletePostForm


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

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('posts',lazy=True))
    comments = db.relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

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
    
    # Get user's teaching connections (as teacher)
    teaching_connections = Connection.query.filter_by(teacher_id=current_user.id).all()
    
    # Get user's learning connections (as learner)
    learning_connections = Connection.query.filter_by(learner_id=current_user.id).all()
    
    # Get active connections (both teaching and learning, where status is 'accepted')
    active_connections = (
        Connection.query
        .filter(
            ((Connection.teacher_id == current_user.id) | (Connection.learner_id == current_user.id)),
            Connection.status == 'accepted'
        )
        .all()
    )
    
    # Get resources relevant to user's skills
    user_skill_ids = [skill.skill_id for skill in teaching_skills + learning_skills]
    resources = Resource.query.filter(Resource.skill_id.in_(user_skill_ids)).all() if user_skill_ids else []
    
    return render_template('dashboard.html', 
                          teaching_skills=teaching_skills,
                          learning_skills=learning_skills,
                          teaching_connections=teaching_connections,
                          learning_connections=learning_connections,
                          active_connections=active_connections,
                          resources=resources)

@app.route('/add-skill', methods=['GET', 'POST'])
@login_required
def add_skill():
    form = SkillForm()
    if form.validate_on_submit():
        # Check if skill already exists
        existing_skill = Skill.query.filter_by(name=form.name.data).first()
        if existing_skill:
            flash('This skill already exists in the system.', 'warning')
            return redirect(url_for('add_user_skill'))
        
        # Create new skill
        skill = Skill(name=form.name.data, description=form.description.data)
        db.session.add(skill)
        db.session.commit()
        
        flash(f'Skill "{form.name.data}" has been added!', 'success')
        return redirect(url_for('add_user_skill'))
        
    return render_template('add_skill.html', form=form)

@app.route('/add-user-skill', methods=['GET', 'POST'])
@login_required
def add_user_skill():
    form = UserSkillForm()
    # Populate the skill select field with available skills
    form.skill.choices = [(skill.id, skill.name) for skill in Skill.query.order_by(Skill.name).all()]
    
    if form.validate_on_submit():
        # Check if the user already has this skill
        existing_user_skill = UserSkill.query.filter_by(
            user_id=current_user.id,
            skill_id=form.skill.data,
            is_teacher=form.is_teacher.data
        ).first()
        
        if existing_user_skill:
            flash('You already have this skill with the same role (teacher/learner).', 'warning')
            return redirect(url_for('dashboard'))
        
        # Create new user skill
        user_skill = UserSkill(
            user_id=current_user.id,
            skill_id=form.skill.data,
            skill_level=form.skill_level.data,
            is_teacher=form.is_teacher.data
        )
        
        db.session.add(user_skill)
        db.session.commit()
        
        role = "teacher" if form.is_teacher.data else "learner"
        skill_name = Skill.query.get(form.skill.data).name
        flash(f'You have been added as a {role} for {skill_name}!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('add_user_skill.html', form=form)

@app.route('/find-connections')
@login_required
def find_connections():
    mode = request.args.get('mode', 'teachers')
    skill_id = request.args.get('skill_id', type=int)
    
    # Get all skills for the dropdowns
    skills = Skill.query.order_by(Skill.name).all()
    
    # If a skill is selected, find matching users
    users = []
    selected_skill = None
    if skill_id:
        selected_skill = Skill.query.get_or_404(skill_id)
        
        if mode == 'teachers':
            # Find users who can teach this skill
            users = UserSkill.query.filter_by(
                skill_id=skill_id,
                is_teacher=True
            ).all()
        else:
            # Find users who want to learn this skill
            users = UserSkill.query.filter_by(
                skill_id=skill_id,
                is_teacher=False
            ).all()
    
    return render_template('find_connections.html', 
                          skills=skills,
                          users=users,
                          selected_skill=selected_skill)

@app.route('/request-connection/<int:user_id>/<int:skill_id>/<string:mode>')
@login_required
def request_connection(user_id, skill_id, mode):
    # Get the target user
    target_user = User.query.get_or_404(user_id)
    skill = Skill.query.get_or_404(skill_id)
    
    # Check if a connection already exists
    existing_connection = None
    if mode == 'teachers':
        # Current user wants to learn from target user
        existing_connection = Connection.query.filter_by(
            teacher_id=user_id,
            learner_id=current_user.id,
            skill_id=skill_id
        ).first()
    else:
        # Current user wants to teach target user
        existing_connection = Connection.query.filter_by(
            teacher_id=current_user.id,
            learner_id=user_id,
            skill_id=skill_id
        ).first()
    
    if existing_connection:
        flash(f'A connection request for this skill already exists.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Create the connection based on the mode
    if mode == 'teachers':
        # Current user wants to learn from target user
        connection = Connection(
            teacher_id=user_id,
            learner_id=current_user.id,
            skill_id=skill_id,
            status='pending'
        )
        flash_message = f'Learning request sent to {target_user.username} for {skill.name}!'
    else:
        # Current user wants to teach target user
        connection = Connection(
            teacher_id=current_user.id,
            learner_id=user_id,
            skill_id=skill_id,
            status='pending'
        )
        flash_message = f'Teaching offer sent to {target_user.username} for {skill.name}!'
    
    db.session.add(connection)
    db.session.commit()
    flash(flash_message, 'success')
    
    return redirect(url_for('dashboard'))
    
@app.route('/handle-connection/<int:connection_id>/<string:action>')
@login_required
def handle_connection(connection_id, action):
    # Get the connection
    connection = Connection.query.get_or_404(connection_id)
    
    # Verify the current user is involved in this connection
    if connection.teacher_id != current_user.id and connection.learner_id != current_user.id:
        flash('You are not authorized to handle this connection request.', 'danger')
        return redirect(url_for('dashboard'))
    
    # For accepting connections, only teachers can accept
    if action == 'accept' and current_user.id != connection.teacher_id:
        flash('Only teachers can accept connection requests.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Handle the action
    if action == 'accept':
        connection.status = 'accepted'
        db.session.commit()
        
        # Get the learner
        learner = User.query.get(connection.learner_id)
        skill = Skill.query.get(connection.skill_id)
        
        flash(f'Connection with {learner.username} for {skill.name} has been accepted!', 'success')
    elif action == 'reject':
        # Both teachers and learners can reject/remove requests
        connection.status = 'rejected'
        db.session.commit()
        
        # Customize message based on who is rejecting
        if current_user.id == connection.teacher_id:
            # Teacher is rejecting the request
            learner = User.query.get(connection.learner_id)
            skill = Skill.query.get(connection.skill_id)
            flash(f'Connection request from {learner.username} for {skill.name} has been rejected.', 'info')
        else:
            # Learner is removing their request
            teacher = User.query.get(connection.teacher_id)
            skill = Skill.query.get(connection.skill_id)
            flash(f'Connection request to {teacher.username} for {skill.name} has been removed.', 'info')
    
    return redirect(url_for('dashboard'))

@app.route('/share-resource', methods=['GET', 'POST'])
@login_required
def share_resource():
    form = ResourceForm()
    # Populate the skill select field with available skills
    form.skill.choices = [(skill.id, skill.name) for skill in Skill.query.order_by(Skill.name).all()]
    
    if form.validate_on_submit():
        # Create new resource
        resource = Resource(
            title=form.title.data,
            description=form.description.data,
            url=form.url.data,
            skill_id=form.skill.data,
            user_id=current_user.id
        )
        
        db.session.add(resource)
        db.session.commit()
        
        flash('Learning resource has been shared successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('share_resource.html', form=form)


@app.route('/community')
def community():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    delete_form = DeletePostForm()
    return render_template('community.html', posts=posts, delete_form=delete_form)

@app.route('/community/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('community'))
    return render_template('new_post.html', form=form)


@app.route('/community/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        content = request.form['content']
        if content:
            comment = Comment(content=content, post_id=post.id, user_id=current_user.id)
            db.session.add(comment)
            db.session.commit()
            flash('Comment added!', 'success')
            return redirect(url_for('post_detail', post_id=post.id))
    delete_form = DeletePostForm()
    return render_template('post_detail.html', post=post, delete_form=delete_form)


@app.route('/community/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('You are not authorized to delete this post.', 'danger')
        return redirect(url_for('post_detail', post_id=post.id))
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect(url_for('community'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)

