from flask import Blueprint, flash, render_template, request, current_app, redirect, url_for, jsonify, session
from flask_jwt_extended import current_user, set_access_cookies, unset_access_cookies, get_current_user
from ...dao.authDAO import AuthDAO
from ...dao.usersDAO import UserDAO
from ...forms import LoginForm, SignUpForm

accounts_routes = Blueprint("accounts", __name__, url_prefix='/')


@accounts_routes.route("/login", methods=["GET", "POST"])
def login():


    login_form = LoginForm()

    if request.method == "POST":
 
        user_name: str = login_form.username.data
        password: str = login_form.password.data

        dao = AuthDAO(current_app.driver, current_app.config.get("JWT_SECRET_KEY"))

        user = dao.login(user_name, password)

        if user is False:
            flash("Usuario o contraseña incorrectos", category="error")
            return render_template("login.html", form=login_form)
        response = redirect(url_for("common.home"))
        set_access_cookies(response, user)
        session["current_user"] = user_name
        return response

    return render_template("login.html", form=login_form)



@accounts_routes.route("/logout", methods=["GET","POST"])
def logout():

    session["current_user"] = None
    if request.method == "GET":
        return redirect(url_for("common.home"))

    response = redirect(url_for("common.home"))
    unset_access_cookies(response)
    return response


@accounts_routes.route("/signup", methods=["GET", "POST"])
def sign_up():

    sign_up_form : SignUpForm = SignUpForm()

    if request.method == "POST":
        
        if sign_up_form.validate_on_submit():

            userDAO = UserDAO(current_app.driver)
            
            user_username = userDAO.get_by_username(sign_up_form.username.data)
            user_email = userDAO.get_by_email(sign_up_form.email.data)
            

            if user_username is None and user_email is None:
                userDAO.create_user(sign_up_form.data)
                session["current_user"] = sign_up_form.username.data
                user = AuthDAO(current_app.driver, current_app.config.get("JWT_SECRET_KEY")).login(sign_up_form.username.data,sign_up_form.password.data)
                response = redirect(url_for("common.home"))
                set_access_cookies(response, user)
                return response
            else:
                flash("El usuario o correo ya existe", category="error")
        else:
            for _, error in sign_up_form.errors.items():    
                for warning in error:
                    flash(warning, category="error")


    return render_template("SignUp.html", form=sign_up_form)
