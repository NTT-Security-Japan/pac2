from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.services.auth_service import add_user, get_user_by_username, get_all_users

auth_bp = Blueprint("auth", __name__, template_folder="templates")

@auth_bp.route("/register",methods=['GET','POST'])
def register():
    # If no pac2 user exists in database OR user is authenticated
    if not get_all_users() or current_user.is_authenticated:
        if request.method == 'POST':
            username = request.form.get("username")
            password = request.form.get("password")
            result = add_user(username=username,password=password)
            if result:
                return redirect(url_for('auth.login'))
            else:
                return render_template('html/register.html.j2', message="Failed to add user.")
        elif request.method == 'GET':
            return render_template('html/register.html.j2')
        else:
            return jsonify({"message": "Method not allowed."}), 405
    return redirect(url_for('auth.login'))

@auth_bp.route("/login",methods=['GET','POST'])
def login():
    if not get_all_users():
        return redirect(url_for('auth.register'))

    if current_user.is_authenticated:
        return redirect(url_for('portal.top'))

    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        pac2user = get_user_by_username(username)

        if pac2user and check_password_hash(pac2user.password, password):
            login_user(pac2user)
            return redirect(url_for('portal.top'))
        else:
            return render_template('html/login.html.j2',message="Login error.")
    elif request.method == 'GET':
        return render_template('html/login.html.j2')
    else:
        return jsonify({"message": "Method not allowed."}), 405

@auth_bp.route("/logout",methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))