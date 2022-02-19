import config
import backend.crypt
from flask import Blueprint, render_template, abort, make_response, request, redirect, url_for, g
from jinja2 import TemplateNotFound

student_page = Blueprint('student_page', __name__, template_folder='templates')

@student_page.route('/account/student', methods=['GET', 'POST'])
def student():
    token = request.cookies.get('jwt')

    if token is None:
        return redirect(url_for('login_page.login'))
    
    decoded_token = backend.crypt.decode_jwt(token)
    type = decoded_token['type']

    if not type == 'student':
        return redirect(url_for('login_page.login'))

    name = decoded_token['first_name']

    print(decoded_token)

    return render_template('student.html', name=name)
