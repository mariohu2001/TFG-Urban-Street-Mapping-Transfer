from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, EmailField

USERNAME_LENGTH = (2, 10)
PASSWORD_LENGTH = (5, 30)


class LoginForm(FlaskForm):

    username = StringField(label="username", validators=[
                           validators.DataRequired()])
    
    password = PasswordField(label="password", validators=[
                             validators.DataRequired()])


class SignUpForm(FlaskForm):

    username = StringField(label="username", validators=[
                           validators.DataRequired(), validators.Length(*USERNAME_LENGTH)])
    
    first_name = StringField(label="first_name")

    surname = StringField(label="surname")

    email = EmailField(label="email", validators=[validators.DataRequired()])

    password = PasswordField(label="password", validators=[
                             validators.DataRequired(), validators.Length(*PASSWORD_LENGTH)])
    
    confirm_password = PasswordField(label="confirm_password", validators=[
                                     validators.DataRequired(), validators.EqualTo(fieldname="password")])
