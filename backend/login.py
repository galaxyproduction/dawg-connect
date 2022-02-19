import config
import backend.crypt
from flask import Blueprint, render_template, abort, make_response, request, redirect, url_for, g
from jinja2 import TemplateNotFound

login_page = Blueprint('login_page', __name__, template_folder='templates')

@login_page.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['pass']

            mycursor = config.mydb.cursor()

            mycursor.execute(f"SELECT uid, password, fname, type FROM User where email='{email}'")

            uid, hashed_pass, fname, type = mycursor.fetchone()

            if not backend.crypt.decrypt_password(password, hashed_pass):
                return render_template('login.html', error='Username or password is incorrect')

            token = backend.crypt.encode_jwt(uid, fname, type)

            if type == 'student':
                resp = make_response(redirect(url_for('student_page.student')))
                resp.set_cookie('jwt', token)
            elif type == 'professor':
                resp = make_response(redirect(url_for('teacher_page.teacher')))
                resp.set_cookie('jwt', token)

            return resp
        else:
            return render_template('login.html')
    except TemplateNotFound:
        abort(404)

@login_page.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login_page.login')))
    resp.delete_cookie('jwt')

    return resp
    