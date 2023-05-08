from flask import Blueprint, render_template, request, current_app, redirect, url_for, jsonify, session
from flask_jwt_extended import set_access_cookies, unset_access_cookies
from ..dao.auth import AuthDAO

accounts_routes = Blueprint("accounts", __name__, url_prefix='/')


@accounts_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
 
        user_name: str = request.form.get("username")
        password: str = request.form.get("password")

        dao = AuthDAO(current_app.driver, current_app.config.get("JWT_SECRET_KEY"))

        user = dao.login(user_name, password)

        if user is False:
            print("malo")
            return render_template("login.html")
        response = redirect(url_for("home"))
        set_access_cookies(response, user)
        session["current_user"] = user_name
        session["is_logged"] = True
        return response

    return render_template("login.html")



@accounts_routes.route("/logout", methods=["POST"])
def logout():
    session["current_user"] = None
    session["is_logged"] = None
    response = redirect(url_for("home"))
    unset_access_cookies(response)
    return response


@accounts_routes.route("/register", methods=["GET", "POST"])
def register():
    return None
