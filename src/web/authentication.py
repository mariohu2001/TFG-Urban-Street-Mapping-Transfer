from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required



def role_required(roles: list):
    def decorator(func):
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = get_jwt_identity()

            if user.get("role") not in roles:
                return jsonify({"msg": "Acceso no autorizado"}), 403

            return func(*args, **kwargs)

        return wrapper

    return decorator
