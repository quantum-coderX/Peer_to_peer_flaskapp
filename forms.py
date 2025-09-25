from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional, URL
from flask_wtf.file import FileAllowed

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class SkillForm(FlaskForm):
    name = StringField('Skill Name', validators=[DataRequired(), Length(min=2, max=50)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Add Skill')

class UserSkillForm(FlaskForm):
    skill = SelectField('Skill', coerce=int, validators=[DataRequired()])
    skill_level = SelectField('Skill Level (1-5)', 
                              choices=[(1, '1 - Beginner'), (2, '2 - Elementary'), (3, '3 - Intermediate'), 
                                       (4, '4 - Advanced'), (5, '5 - Expert')], 
                              coerce=int,
                              validators=[DataRequired(), NumberRange(min=1, max=5)])
    is_teacher = BooleanField('I can teach this skill')
    submit = SubmitField('Add Skill')

class ConnectionRequestForm(FlaskForm):
    message = TextAreaField('Message to Recipient', validators=[Optional(), Length(max=300)])
    submit = SubmitField('Send Request')

class ResourceForm(FlaskForm):
    title = StringField('Resource Title', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    url = StringField('URL (if online resource)', validators=[Optional(), URL()])
    skill = SelectField('Related Skill', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Share Resource')

class ProfileUpdateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Update Profile')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=2)])
    submit = SubmitField('Create')

class DeletePostForm(FlaskForm):
    submit = SubmitField('Delete')