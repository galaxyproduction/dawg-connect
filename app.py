import backend.crypt
from flask import Flask, render_template, request, redirect, url_for, make_response

import config

from backend.login import login_page
from backend.register import register_page
from backend.student import student_page
from backend.teacher import teacher_page
from backend.admin import admin_page

UPLOAD_FOLDER = './resumes'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.register_blueprint(login_page)
app.register_blueprint(register_page)
app.register_blueprint(student_page)
app.register_blueprint(teacher_page)
app.register_blueprint(admin_page)

@app.route('/')
def index():
    token = request.cookies.get('jwt')

    if token is None:
        return redirect(url_for('login_page.login'))
    
    decoded_token = backend.crypt.decode_jwt(token)
    type = decoded_token['type']

    if type == 'student':
        return redirect(url_for('student_page.student'))
    elif type == 'professor':
        return redirect(url_for('teacher_page.teacher'))
    else:
        return  redirect(url_for('admin_page.admin')) 

if __name__ == '__main__':
    config.init()
    app.run(host='0.0.0.0')