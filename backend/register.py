import config
import backend.crypt
from flask import Blueprint, render_template, abort, make_response, request, redirect, url_for
from jinja2 import TemplateNotFound
from datetime import datetime

register_page = Blueprint('register_page', __name__,
                          template_folder='templates')


@register_page.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            email = request.form['email']
            password = request.form['pass']
            confirm_password = request.form['confPass']

            if password != confirm_password:
                return render_template('register.html', error='Passwords do not match')

            encryptedPass = backend.crypt.encrypt_password(password)
            mycursor = config.mydb.cursor()

            sql = "INSERT INTO User (email, fname, lname, password, type) VALUES (%s, %s, %s, %s, %s)"
            val = (email, fname, lname, encryptedPass, 'professor')
            mycursor.execute(sql, val)

            config.mydb.commit()

            token = backend.crypt.encode_jwt(
                mycursor.lastrowid, fname, 'student')

            resp = make_response(redirect(url_for('student_page.student')))
            resp.set_cookie('jwt', token)

            return resp
        else:
            return render_template('register.html', account_type='Student Account')
    except TemplateNotFound:
        abort(404)


@register_page.route('/register/<temp_url>', methods=['GET', 'POST'])
def teacher_register(temp_url):
    try:
        mycursor = config.mydb.cursor()

        sql = f"SELECT expirationDate FROM ProfessorUrl WHERE url='{temp_url}'"
        mycursor.execute(sql)
        expiration = mycursor.fetchone()

        if expiration is None or datetime.now() > expiration[0]:
            return render_template('register.html', error='Invalid link or link has expired')

        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            email = request.form['email']
            password = request.form['pass']
            confirm_password = request.form['confPass']

            if password != confirm_password:
                return render_template('register.html', error='Passwords do not match')

            encryptedPass = backend.crypt.encrypt_password(password)
            mycursor = config.mydb.cursor()

            sql = "INSERT INTO User (email, fname, lname, password, type) VALUES (%s, %s, %s, %s, %s)"
            val = (email, fname, lname, encryptedPass, 'professor')
            mycursor.execute(sql, val)

            config.mydb.commit()

            token = backend.crypt.encode_jwt(
                mycursor.lastrowid, fname, 'teacher')

            resp = make_response(redirect(url_for('teacher_page.teacher')))
            resp.set_cookie('jwt', token)

            return resp
        else:
            return render_template('register.html', account_type='Professor Account')
    except TemplateNotFound:
        abort(404)
