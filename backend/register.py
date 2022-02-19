import config
import backend.crypt
from flask import Blueprint, render_template, abort, make_response, request, redirect, g
from jinja2 import TemplateNotFound

register_page = Blueprint('register_page', __name__, template_folder='templates')

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

            token = backend.crypt.encode_jwt(mycursor.lastrowid, fname, 'student')

            resp = make_response(redirect('/account/student'))
            resp.set_cookie('jwt', token)

            return resp
        else:
            return render_template('register.html')
    except TemplateNotFound:
        abort(404)