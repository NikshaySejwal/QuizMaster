from controller.database import db   
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    

   



class subjects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),nullable=False)
   

class chapters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
   
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
    sub=db.relationship('subjects',backref='chapters')



class quizs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    time_limit = db.Column(db.Integer, nullable=False)
    subject = db.relationship('subjects', backref=db.backref('quizs'))
    chapter = db.relationship('chapters', backref=db.backref('quizs'))

    chapter = db.relationship('chapters', backref=db.backref('quizs'))


class questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizs.id'), nullable=False)
    text = db.Column(db.String(80), nullable=False)
    option1 = db.Column(db.String(80), nullable=False)
    option2 = db.Column(db.String(80), nullable=False)
    option3 = db.Column(db.String(80), nullable=False)
    option4 = db.Column(db.String(80), nullable=False)
    answer = db.Column(db.String(80), nullable=False)
    
    

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizs.id'), nullable=False)  # Link to quiz
    user_email = db.Column(db.String,db.ForeignKey('user.email'), nullable=False) 
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)  # Store total questions
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) 

    quiz = db.relationship('quizs', backref='Score')  # Optional, for easy querying
    user = db.relationship('User', backref='Score')







    