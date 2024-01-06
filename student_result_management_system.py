from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
import os

class Config:
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/db_name'


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

import os



class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    family_name = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(100), nullable=False)

@app.route('/')
def home():
    return render_template('index.html')




def validate_date_of_birth(dob):
    try:
        dob_date = datetime.strptime(dob, '%Y-%m-%d')
        age = datetime.now() - dob_date
        if age < timedelta(days=3650):  # Minimum age of 10 years
            flash('Student must be at least 10 years old.', 'error')
            return False
        return True
    except ValueError:
        return False


def validate_email(email):
    return '@' in email and '.' in email.split('@')[1]




@app.route('/add_students', methods=['GET', 'POST'])
def add_students():


    if request.method == 'POST':
        first_name = request.form['first_name']
        family_name = request.form['family_name']
        dob = request.form['dob']
        email = request.form['email']

        if not all([first_name, family_name, dob, email]):
            flash('All fields must be filled.', 'error')
        elif not validate_date_of_birth(dob):
            flash('Invalid date of birth or student must be at least 10 years old.', 'error')
        elif not validate_email(email):
            flash('Invalid email address.', 'error')
        else:
            new_student = Student(first_name=first_name, family_name=family_name, dob=dob, email=email)
            db.session.add(new_student)
            db.session.commit()  
            print("After commit:", new_student) 

            flash('New student added successfully!', 'success')
            return redirect(url_for('add_students'))


    return render_template('add_students.html')




@app.route('/students_list')
def students_list():

    students = Student.query.all()

    return render_template('students_list.html', students=students)





@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        Result.query.filter_by(student_id=student_id).delete()

        db.session.delete(student)
        db.session.commit()

        flash('Student deleted successfully!', 'success')
    else:
        flash('Student not found!', 'error')

    return redirect(url_for('students_list'))



class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)


@app.route('/add_courses', methods=['GET', 'POST'])
def add_courses():
    if request.method == 'POST':
        course_name = request.form['course_name']

        if not course_name:
            flash('Course name must be filled.', 'error')
        else:
            new_course = Course(course_name=course_name)
            db.session.add(new_course)
            db.session.commit()

            flash('New course added successfully!', 'success')

            return redirect(url_for('add_courses'))

    return render_template('add_courses.html')

@app.route('/courses_list')
def courses_list():
    courses = Course.query.all()
    return render_template('courses_list.html', courses=courses)


@app.route('/delete_course/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    course = Course.query.get(course_id)
    if course:
        Result.query.filter_by(course_id=course_id).delete()

        db.session.delete(course)
        db.session.commit()

        flash('Course deleted successfully!', 'success')
    else:
        flash('Course not found!', 'error')

    return redirect(url_for('courses_list'))




class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    score = db.Column(db.String(1), nullable=False)

    course = db.relationship('Course', backref=db.backref('results', lazy=True))
    student = db.relationship('Student', backref=db.backref('results', lazy=True))

@app.route('/add_results', methods=['GET', 'POST'])
def add_results():
    if request.method == 'POST':
        course_id = request.form['course']
        student_id = request.form['student']
        score = request.form['score']

        if not all([course_id, student_id, score]):
            flash('Please select a course, a student, and a score.', 'error')
        else:
            new_result = Result(course_id=course_id, student_id=student_id, score=score)
            db.session.add(new_result)
            db.session.commit()

            flash('New result added successfully!', 'success')

            return redirect(url_for('add_results'))

    courses = Course.query.all()
    students = Student.query.all()

    return render_template('add_results.html', courses=courses, students=students)

@app.route('/results_list')
def results_list():
    results = Result.query.join(Course).join(Student).filter(Student.id.isnot(None), Course.id.isnot(None)).all()
    return render_template('results_list.html', results=results)


if __name__ == '__main__':
	with app.app_context():
        	db.create_all()
	        print("Data stored successfully")

	app.run(debug=True)
