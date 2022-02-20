import config
import backend.crypt
from flask import Blueprint, render_template, abort, make_response, request, redirect, url_for, g
from jinja2 import TemplateNotFound
from datetime import datetime, timedelta

admin_page = Blueprint('admin_page', __name__, template_folder='templates')


@admin_page.route('/account/admin/generate', methods=['POST'])
def generate_link():
    url = request.get_json()
    expiration = datetime.now() + timedelta(hours=3)
    mycursor = config.mydb.cursor()

    sql = "INSERT INTO ProfessorUrl (url, expirationDate) VALUES (%s, %s)"
    val = (url['url'], expiration)
    mycursor.execute(sql, val)

    config.mydb.commit()

    return 'Success'

@admin_page.route('/account/admin', methods=['GET', 'POST'])
def admin():
    token = request.cookies.get('jwt')

    if token is None:
        return redirect(url_for('login_page.login'))

    decoded_token = backend.crypt.decode_jwt(token)
    type = decoded_token['type']
    uid = decoded_token['uid']
    name = decoded_token['first_name']

    if not type == 'admin':
        return redirect(url_for('login_page.login'))

    mycursor = config.mydb.cursor()

    sql = f"SELECT COUNT(aid) FROM Application"
    mycursor.execute(sql)
    appCount = mycursor.fetchone()

    mycursor = config.mydb.cursor()

    sql = f"SELECT COUNT(pid) FROM Position"
    mycursor.execute(sql)
    posCount = mycursor.fetchone()

    stats = { 'jobs': posCount[0], 'applicants': appCount[0]}

    mycursor = config.mydb.cursor()

    sql = f"SELECT * FROM Application app INNER JOIN User user on user.uid=app.uid"
    mycursor.execute(sql)
    studentResults = mycursor.fetchall()

    labels = ('aid', 'uid', 'major', 'gpa', 'essay', 'resume', 'firstPick', 'secondPick', 'thirdPick', 'uid', 'fname', 'lname', 'email')
    students = []
    for student in studentResults:
        students.append(dict(map(lambda x,y: (x, y), labels, student)))

    sql = f"SELECT * FROM Position pos INNER JOIN User user on pos.professor = user.uid"
    if request.args.get('searchBy'):
        searchBy = request.args.get('searchBy')
        sql = f"""
            SELECT * FROM Position pos INNER JOIN User user on pos.professor = user.uid WHERE
            user.fname LIKE '%{searchBy}%' OR user.lname LIKE '%{searchBy}%' OR user.email LIKE '%{searchBy}%'
            OR pos.course LIKE '%{searchBy}%' OR pos.description LIKE '%{searchBy}%'
            """

    mycursor.execute(sql)
    courseResults = mycursor.fetchall()

    labels = ('pid', 'professor', 'course', 'description', 'location',
                'startTime', 'endTime', 'uid', 'fname', 'lname', 'email')
    courses = []
    for course in courseResults:
        courses.append(dict(map(lambda x, y: (x, y), labels, course)))

    return render_template('admin.html', name=name, students=students, courses=courses, stats=stats)
