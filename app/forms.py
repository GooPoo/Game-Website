from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError

def validate_username(form, field):
    if not field.data.isalpha():
        raise ValidationError('Username must only contain alphabetic characters.')
    if len(field.data) < 3 or len(field.data) > 20:
        raise ValidationError('Username must be between 3 and 20 characters long.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), validate_username])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign in')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), validate_username])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

class TokenForm(FlaskForm):
    generate_token = SubmitField('Generate Token')
    revoke_token = SubmitField('Revoke Token')