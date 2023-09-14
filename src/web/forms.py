from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, EmailField

USERNAME_LENGTH = (2, 20)
PASSWORD_LENGTH = (4, 30)


class LoginForm(FlaskForm):

    username = StringField(label="Nombre de usuario", validators=[
                           validators.DataRequired()])

    password = PasswordField(label="Contraseña", validators=[
                             validators.DataRequired()])


class SignUpForm(FlaskForm):

    username = StringField(label="Nombre de usuario", validators=[
                           validators.DataRequired(), validators.Length(*USERNAME_LENGTH,
                                                                        f"""El nombre de usuario debe de tener entre {USERNAME_LENGTH[0]}  y {USERNAME_LENGTH[1]} """)])

    first_name = StringField(label="Nombre")

    surname = StringField(label="Apellido")

    email = EmailField(label="Correo electrónico", validators=[validators.DataRequired("Por favor inserte su correo electrónico")])

    password = PasswordField(label="Contraseña", validators=[
                             validators.DataRequired(), validators.Length(*PASSWORD_LENGTH,
                                                                          f"La contraseña debe de estar entre {PASSWORD_LENGTH[0]} y {PASSWORD_LENGTH[1]} caracteres")])

    confirm_password = PasswordField(label="Confirmar Contraseña", validators=[
                                     validators.DataRequired(), validators.EqualTo(fieldname="password", message="Las contraseñas no coinciden")])
