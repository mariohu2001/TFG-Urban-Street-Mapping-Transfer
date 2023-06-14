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
                           validators.DataRequired(), validators.Length(*USERNAME_LENGTH,
                                                                        f"""El nombre de usuario debe de tener entre {USERNAME_LENGTH[0]}  y {USERNAME_LENGTH[1]} """)])

    first_name = StringField(label="first_name")

    surname = StringField(label="surname")

    email = EmailField(label="email", validators=[validators.DataRequired("Por favor inserte su correo electrónico")])

    password = PasswordField(label="password", validators=[
                             validators.DataRequired(), validators.Length(*PASSWORD_LENGTH,
                                                                          f"La contraseña debe de estar entre {PASSWORD_LENGTH[0]} y {PASSWORD_LENGTH[1]} caracteres")])

    confirm_password = PasswordField(label="confirm_password", validators=[
                                     validators.DataRequired(), validators.EqualTo(fieldname="password", message="Las contraseñas no coinciden")])
