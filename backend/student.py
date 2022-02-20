import os
from re import search
import config
import backend.crypt
from flask import Blueprint, render_template, abort, make_response, request, redirect, url_for, g
from jinja2 import TemplateNotFound
from werkzeug.utils import secure_filename
from datetime import datetime

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
    uid = decoded_token['uid']

    mycursor = config.mydb.cursor()
    sql = f"SELECT * FROM Application app INNER JOIN User user ON app.uid = user.uid WHERE app.uid={uid}"
    mycursor.execute(sql)
    applicationResult = mycursor.fetchone()

    labels = ('aid', 'uid', 'major', 'gpa', 'essay', 'resume', 'firstPick', 'secondPick', 'thirdPick', 'uid', 'fname', 'lname', 'email')
    
    application = dict()
    if not applicationResult is None:
        application = dict(map(lambda x,y: (x, y), labels, applicationResult))

        mycursor = config.mydb.cursor()
        sql = f"SELECT course FROM Position WHERE pid={application['firstPick']}"
        mycursor.execute(sql)
        firstPick = mycursor.fetchone()

        application['firstPick'] = firstPick[0]

        mycursor = config.mydb.cursor()
        sql = f"SELECT course FROM Position WHERE pid={application['secondPick']}"
        mycursor.execute(sql)
        secondPick = mycursor.fetchone()

        application['secondPick'] = secondPick[0]

        mycursor = config.mydb.cursor()

        sql = f"SELECT course FROM Position WHERE pid={application['thirdPick']}"
        mycursor.execute(sql)
        thirdPick = mycursor.fetchone()

        application['thirdPick'] = thirdPick[0]

        sql = f"SELECT * FROM Skill WHERE uid={uid}"
        mycursor.execute(sql)
        skillResult = mycursor.fetchall()

        application['skills'] = list(map(lambda tup: tup[2], skillResult))

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

    labels = ('pid', 'professor', 'course', 'description', 'location', 'startTime', 'endTime', 'uid', 'fname', 'lname', 'email')
    courses = []
    for course in courseResults:
        courses.append(dict(map(lambda x,y: (x, y), labels, course)))

    return render_template('student.html', name=name, application=application, courses=courses)

@student_page.route('/account/application', methods=['GET', 'POST'])
def application():
    token = request.cookies.get('jwt')

    if token is None:
        return redirect(url_for('login_page.login'))
    
    decoded_token = backend.crypt.decode_jwt(token)
    type = decoded_token['type']
    uid = decoded_token['uid']

    if not type == 'student':
        return redirect(url_for('login_page.login'))

    name = decoded_token['first_name']

    mycursor = config.mydb.cursor()

    mycursor.execute(f"SELECT pid, course from Position")

    courses = mycursor.fetchall()

    if request.method == 'POST':
        major = request.form['major']
        gpa = request.form['gpa']
        essay = request.form['essay']
        firstPick = request.form['firstPick']
        secondPick = request.form['secondPick']
        thirdPick = request.form['thirdPick']

        file = request.files['resume']
        filename = str(datetime.now()) + '_' + secure_filename(file.filename)
        file.save(os.path.join('static/resumes', filename))

        mycursor = config.mydb.cursor()
        sql = "INSERT INTO Application (uid, major, gpa, essay, resume, firstPick, secondPick, thirdPick) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (uid, major, gpa, essay, filename, firstPick, secondPick, thirdPick)
        mycursor.execute(sql, val)

        config.mydb.commit()

        sql = "INSERT INTO Skill (uid, skill) VALUES (%s, %s)"
        skills = []
        for skill in request.form.to_dict(flat=False)['skills']:
            skills.append((uid, skill))

        mycursor = config.mydb.cursor()
        mycursor.executemany(sql, skills)
        config.mydb.commit()

        return redirect(url_for('student_page.student'))

    return render_template('application.html', name=name, courses=courses)

