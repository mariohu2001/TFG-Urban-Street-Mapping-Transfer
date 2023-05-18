from flask import Blueprint, flash, render_template, request, current_app, redirect, url_for, jsonify, session
from flask_jwt_extended import current_user, set_access_cookies, unset_access_cookies, get_current_user
from ..dao.auth import AuthDAO
from ..forms import LoginForm, SignUpForm

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
            print("malo")
            # login_form.error.user_name.append("Usuario o contraseña incorrectos")
            return render_template("login.html", form=login_form)
        response = redirect(url_for("home"))
        set_access_cookies(response, user)
        print(get_current_user())
        session["current_user"] = user_name
        session["is_logged"] = True
        return response

    return render_template("login.html", form=login_form)



@accounts_routes.route("/logout", methods=["POST"])
def logout():
    # session["current_user"] = None
    # session["is_logged"] = None
    response = redirect(url_for("home"))
    unset_access_cookies(response)
    return response


@accounts_routes.route("/signup", methods=["GET", "POST"])
def sign_up():
    return None
