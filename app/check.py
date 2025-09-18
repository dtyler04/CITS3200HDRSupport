from functools import wraps
from flask import redirect, url_for, flash, session,abort
from .models import User, Right

def login_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if 'uid' not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("main.login_page"))
        return func(*args, **kwargs)
    return wrapped

def login_and_rights_required(*perm_numbers):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            uid = session.get('uid')
            if not uid:
                flash("Please log in first.", "warning")
                return redirect(url_for("main.login_page"))

            user = User.query.get(uid)
            if not user:
                abort(403)

            user_perm_numbers = {r.permission_number for r in Right.query.filter_by(user_id=uid).all()}
            if not user_perm_numbers.intersection(set(perm_numbers)):
                abort(403)

            return f(*args, **kwargs)
        return wrapped
    return decorator