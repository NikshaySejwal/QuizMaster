from collections import defaultdict
from app import app
from flask import render_template, request, session, redirect, url_for, flash,Blueprint
from datetime import datetime , timedelta
from models import * 
import matplotlib.pyplot as plt
import matplotlib
import io
import base64
from io import BytesIO
matplotlib.use('Agg')

# view = Blueprint('main', __name__)
@app.route('/')
def home():
    # sub= subjects.query.all()
    return render_template('home.html') 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    
    if request.method == "POST":
        email = request.form.get('email', None)
        password = request.form.get('password', None)
       
        #data vaildation

        if not email or not password:
            # return error message
            flash('Please Sign up first')
            return render_template('login.html')
        
        email = User.query.filter_by(email = email).all()
        if not email:
            ## return error message
            flash('Email not found')
            return render_template('sign_up.html')
        
        if email[0].password != password:
            ## return error message
            flash('Password incorrect')
            return render_template('login.html')
        
        session['user_email'] = email[0].email
        return redirect('/')


@app.route('/logout')
def logout():
    # session.pop('user_email', None)
    # session.pop('role', None)
    session.clear()
    return redirect(url_for('login'))  

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == "GET":
        return render_template('sign_up.html')  

    if request.method == "POST":   
        name = request.form.get('name', None)
        email = request.form.get('email', None)
        password = request.form.get('password', None)
        # role = request.form.get('role', None)
        confirm_password = request.form.get('confirm_password', None)

        # data validation

        if not name or not email or not password or not confirm_password:
            flash('Please fill all fields')
            return render_template('sign_up.html')
        
        if password != confirm_password:
            flash('Password does not match')
            return render_template('sign_up.html')
        
        if User.query.filter_by(email = email).all():
            flash('Email already exists')
            return render_template('login.html')
        
        user = User(
            username = name,
            email = email,
            password = password,
            # roles = [Role.query.filter_by(name = role).first()],
            # roles = Role.query.filter_by(name = role).all()

        )

        db.session.add(user)
        db.session.commit()

        flash('User created successfully')
        return redirect('/login')






@app.route('/manage_user')
def manage_users():
    if session.get('user_email') != 'admin@gmail.com':
        flash('Unauthorized Access')
        return redirect(url_for('home'))

    users = User.query.filter(User.email != 'admin@gmail.com').all()

    # Fetch quiz scores and generate charts
    scores = (
        db.session.query(
            Score.quiz_id,
            Score.score,
            quizs.name.label('quiz_name'),
            subjects.name.label('subject_name')
        )
        .join(quizs, Score.quiz_id == quizs.id)
        .join(subjects, quizs.subject_id == subjects.id)
        .all()
    )

    # Process scores for average scores per subject (Bar Chart)
    subject_scores = defaultdict(list)
    for score in scores:
        subject_scores[score.subject_name].append(score.score)

    subjects_list = list(subject_scores.keys())
    avg_scores = [sum(subject_scores[subj]) / len(subject_scores[subj]) for subj in subjects_list]

    fig, ax = plt.subplots()
    ax.bar(subjects_list, avg_scores, color='blue')
    ax.set_title("Subject-wise Average Scores")
    ax.set_xlabel('Subjects')
    ax.set_ylabel('Average Score')

    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    bar_chart = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # Process scores for line chart (Score Trends)
    quiz_names = [score.quiz_name for score in scores]
    scores_list = [score.score for score in scores]

    fig, ax = plt.subplots()
    ax.plot(quiz_names, scores_list, marker='o', color='green')
    ax.set_title("Score Trends Over Quizzes")
    ax.set_xlabel('Quizzes')
    ax.set_ylabel('Scores')
    plt.xticks(rotation=45)

    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    line_chart = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return render_template('manage_user.html', users=users, bar_chart=bar_chart, line_chart=line_chart)




    
@app.route('/delete_user/<int:id>')
def delete_user(id):
    if not session.get('user_email',None)=='admin@gmail.com':
        flash("Unauthorized Acessces")
        return redirect (url_for('home'))
    user=User.query.get(id)

    if not user:
        flash ('User not found')
        return redirect(url_for('manage_user')) 

    db.session.delete(user)
    db.session.commit()

    flash('User deleted successfully')
    return redirect(url_for('manage_users'))   



@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if not session.get('user_email',None) == 'admin@gmail.com':
        flash('Unauthorized Access')
        return redirect(url_for('home'))
    
    if request.method == "GET":
        all_subjects=subjects.query.all()
        return render_template('add_subject.html',subjects=all_subjects)
    
    if request.method == "POST":
        name = request.form.get('name', None)
        # description = request.form.get('description', None)

        if not name :
            flash('Please fill all fields')
            return render_template('add_subject.html')
        
        existing_subject = subjects.query.filter_by(name=name).first()
        if existing_subject:
            flash('subject already exists')
            all_subjects=subjects.query.all()
            return render_template('add_subject.html',subjects=all_subjects)
        
        
        new_subject = subjects(name=name)
        db.session.add(new_subject)
        db.session.commit()

        flash('Subject added successfully')
        all_subjects=subjects.query.all()
        return render_template('add_subject.html',subjects=all_subjects)




@app.route('/edit_subject/<int:id>', methods=['GET', 'POST'])
def edit_subject(id):
    if not session.get('user_email',None)=='admin@gmail.com':
        flash('Unauthorized Access')
        return redirect(url_for('home'))
    
    subject = subjects.query.get(id)
    if not subject:
        flash('subject not found')
        return redirect(url_for('add_subject'))
    
    if request.method == "GET":
        # print(sub)
        return render_template('edit_subject.html', subject = subject)
    
    if request.method == "POST":
        name = request.form.get('name', None)
        # description = request.form.get('description', None)

        if not name:
            flash('please fill all fields')
            return redirect(url_for('edit_subject',id=subject.id))
        

        subject.name=name
        db.session.commit()

        flash('subject updated successfully')
        return redirect(url_for('add_subject',id=subject.id))



@app.route('/delete_subject/<int:id>')
def delete_subject(id):
    if not session.get('user_email') == 'admin@gmail.com':
        flash('Unauthorized Access', 'danger')
        return redirect(url_for('home'))
    
    subject = subjects.query.get_or_404(id)

    # Delete all related chapters, quizzes, questions, and scores
    chapters_to_delete = chapters.query.filter_by(subject_id=id).all()

    for chapter in chapters_to_delete:
        quizzes_to_delete = quizs.query.filter_by(chapter_id=chapter.id).all()
        for quiz in quizzes_to_delete:
            # Delete related scores first
            Score.query.filter_by(quiz_id=quiz.id).delete()
            # Delete related questions
            questions.query.filter_by(quiz_id=quiz.id).delete()
            # Delete the quiz
            db.session.delete(quiz)
        db.session.delete(chapter)

    db.session.delete(subject)
    db.session.commit()

    flash("Subject and all associated chapters, quizzes, questions, and scores deleted successfully.", "success")
    return redirect(url_for('add_subject'))








@app.route('/add_chapter', methods=['GET', 'POST'])
def add_chapter():
    if not session.get('user_email',None)=='admin@gmail.com':
        flash('unauthorized Access')
        return redirect(url_for('home'))
    if request.method=='GET':
        all_subjects=subjects.query.all()
        all_chapter=chapters.query.all()
        return render_template('add_chapter.html',subjects = all_subjects,chapters=all_chapter)
    if request.method == 'POST':
        chapter_name = request.form.get('name')
        subject_id=request.form.get('subject')

        if not chapter_name or not subject_id:
            flash('please fill all fields')
            return redirect(url_for('add_chapter'))  
        new_chapter = chapters(name=chapter_name, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        flash(' New chapter is added ')
        all_subjects=subjects.query.all()
        all_chapter=chapters.query.all()
        return render_template('add_chapter.html',subjects = all_subjects,chapters=all_chapter)

@app.route('/edit_chapter/<int:id>', methods=['GET', 'POST'])
def edit_chapter(id):
    if session.get('user_email') != 'admin@gmail.com':
        flash('Unauthorized Access')
        return redirect(url_for('home'))

    chapter = chapters.query.get_or_404(id)

    if request.method == "POST":
        chapter.name = request.form.get('name')
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('add_chapter'))

    return render_template('edit_chapter.html', chapter=chapter)



@app.route('/delete_chapter/<int:id>')
def delete_chapter(id):
    if not session.get('user_email') == 'admin@gmail.com':
        flash('Unauthorized Access', 'danger')
        return redirect(url_for('home'))
    
    chapter = chapters.query.get_or_404(id)

    quiz=quizs.query.filter_by(chapter_id=id).all()  # Delete all quizzes under this chapter
    for quizers in quiz:
        questions.query.filter_by(quiz_id=id).delete()
        db.session.delete(quizers)


    db.session.delete(chapter)
    db.session.commit()
    flash("Chapter and all associated quizzes deleted successfully.", "success")
    return redirect(url_for('add_chapter'))













@app.route('/add_question/<int:quiz_id>', methods=['GET', 'POST'])
def add_question(quiz_id):
    quiz = quizs.query.get(quiz_id)  # Fetch quiz using quizs model

    if not quiz:
        flash("Quiz not found.", "danger")
        return redirect(url_for('create_quiz'))

    if request.method == 'POST':
        text = request.form['text']  # Required field
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']

        if not text or not option1 or not option2 or not option3 or not option4 or not answer:
            flash("Please fill all fields.", "danger")
            return redirect(url_for('add_question', quiz_id=quiz_id))

        
        new_question = questions(
            quiz_id=quiz_id, 
            text=text,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            answer=answer
        )

        db.session.add(new_question)
        db.session.commit()

        flash("Question added successfully!", "success")
        return redirect(url_for('add_question', quiz_id=quiz_id))  
    Question = questions.query.filter_by(quiz_id=quiz_id).all()
    return render_template('add_question.html', quiz=quiz,Question=Question)


@app.route('/edit_question/<int:id>', methods=['GET', 'POST'])
def edit_question(id):
    ques = questions.query.get_or_404(id)

    if request.method == 'POST':
        ques.text = request.form['text']
        ques.option1 = request.form['option1']
        ques.option2 = request.form['option2']
        ques.option3 = request.form['option3']
        ques.option4 = request.form['option4']
        ques.answer = request.form['answer']

        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('add_question',quiz_id=ques.quiz_id))

    return render_template('edit_question.html', ques=ques)




@app.route('/delete_question/<int:id>')
def delete_question(id):  # Parameter name should match route
    if session.get('user_email') != 'admin@gmail.com':  # Restrict access to admin
        flash('Unauthorized Access', 'danger')
        return redirect(url_for('home'))

    ques = questions.query.get_or_404(id)  # Ensure correct model name
    db.session.delete(ques)
    db.session.commit()

    flash('Question deleted successfully!', 'success')
    return redirect(url_for('add_question',quiz_id=ques.quiz_id))  # Redirect instead of rendering





@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if session.get('user_email') != 'admin@gmail.com':
        flash('Unauthorized access')
        return redirect(url_for('home'))
    
    all_subjects = subjects.query.all()
    selected_subject_id = request.args.get('subject', type=int)  # Get selected subject from dropdown
    filtered_chapters = chapters.query.filter_by(subject_id=selected_subject_id).all() if selected_subject_id else []

    if request.method == 'POST':
        quiz_name = request.form.get('name')
        subject_id = request.form.get('subject')
        chapter_id = request.form.get('chapter')
        time_limit = request.form.get('time_limit')

        if not quiz_name or not subject_id or not chapter_id or not time_limit:
            flash('Please fill all fields', 'danger')
            return redirect(url_for('create_quiz'))

        new_quiz = quizs(
            name=quiz_name,
            subject_id=subject_id,
            chapter_id=chapter_id,
            time_limit=time_limit
        )
        db.session.add(new_quiz)
        db.session.commit()

        flash('Quiz created successfully! Now add questions.', 'success')
        return redirect(url_for('create_quiz', quiz_id=new_quiz.id))  # Redirect to add questions

    return render_template('create_quiz.html', subjects=all_subjects, chapters=filtered_chapters, selected_subject_id=selected_subject_id)

    

    
@app.route('/edit_quiz/<int:id>', methods=['GET', 'POST'])
def edit_quiz(id):
    quiz = quizs.query.get_or_404(id)

    if request.method == "POST":
        quiz.name = request.form['name']
        quiz.time_limit = int(request.form['time_limit'])  # Ensure it's stored as an integer
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('create_quiz')) 

    return render_template('edit_quiz.html', quiz=quiz)



@app.route('/delete_quiz/<int:quiz_id>')
def delete_quiz(quiz_id):
    # Check if the user is logged in and has the 'admin' role
    if not session.get('user_email') == 'admin@gmail.com':
        flash('Unauthorized Access', 'danger')
        return redirect(url_for('home'))

    
    quiz = quizs.query.get(quiz_id)
    # score=Score.query.get(quiz_id)
    
    if not quiz:
        flash('Quiz not found.', 'danger')
        return redirect(url_for('create_quiz'))  # Redirect if quiz doesn't exist

    
    questions.query.filter_by(quiz_id=quiz_id).delete()
    Score.query.filter_by(quiz_id=quiz_id).delete()

    # Now delete the quiz
    db.session.delete(quiz)
    # db.session.delete(score)
    db.session.commit()

    flash("Quiz deleted successfully!", "danger")
    return redirect(url_for('create_quiz'))  # Redirect back to the add_quiz page






@app.route('/attempt_quiz', methods=['GET', 'POST'])
def attempt_quiz():
    all_subjects = subjects.query.all()  # Avoid conflict by renaming variable

    selected_subject_id = request.args.get('subject_id', type=int)
    selected_chapter_id = request.args.get('chapter_id', type=int)

    filtered_chapters = []
    filtered_quizs = []

    if selected_subject_id:
        filtered_chapters = chapters.query.filter_by(subject_id=selected_subject_id).all()
    
    if selected_chapter_id:
        filtered_quizs = quizs.query.filter_by(chapter_id=selected_chapter_id).all()

    return render_template(
        'attempt_quiz.html',
        subjects=all_subjects,  # Using renamed variable
        chapters=filtered_chapters,
        quizs=filtered_quizs,
        selected_subject_id=selected_subject_id,
        selected_chapter_id=selected_chapter_id
    )




@app.route('/view_scores')
def view_scores():
    if 'user_email' not in session:
        flash("Please log in to view scores.", "danger")
        return redirect(url_for('login'))

    user_email = session['user_email']
    user = User.query.filter_by(email=user_email).first()

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('login'))

    scores = (
        db.session.query(
            subjects.name.label("subject_name"),
            chapters.name.label("chapter_name"),
            quizs.name.label("quiz_name"),
            Score.score,
            Score.timestamp
        )
        .join(chapters, subjects.id == chapters.subject_id)
        .join(quizs, chapters.id == quizs.chapter_id)
        .join(Score, quizs.id == Score.quiz_id)
        .filter(Score.user_email == user_email)  
        .all()
    )
# Data for visualization
    quiz_names = [score.quiz_name for score in scores]
    scores_data = [score.score for score in scores]

    # Generate Bar Chart
    fig, ax = plt.subplots()
    ax.bar(quiz_names, scores_data, color='skyblue')
    ax.set_xlabel('Quizzes')
    ax.set_ylabel('Scores')
    ax.set_title('Scores by Quiz')

    # Save Bar Chart to Base64
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    bar_chart = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close(fig)

    # Generate Line Chart
    fig, ax = plt.subplots()
    ax.plot(quiz_names, scores_data, marker='o', linestyle='-', color='orange')
    ax.set_xlabel('Quizzes')
    ax.set_ylabel('Scores')
    ax.set_title('Score Trend Over Quizzes')

    # Save Line Chart to Base64
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    line_chart = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close(fig)

    return render_template('view_scores.html', scores=scores, bar_chart=bar_chart, line_chart=line_chart)










@app.route('/start_quiz/<int:quiz_id>')
def start_quiz(quiz_id):
    quiz = quizs.query.get_or_404(quiz_id)  # Fetch the quiz
    quiz_ques = questions.query.filter_by(quiz_id=quiz.id).all()  # Get questions

    if not quiz_ques:
        flash("No questions available for this quiz.", "warning")
        return redirect(url_for('attempt_quiz'))  # Redirect back if no questions

    return render_template('start_quiz.html', quiz=quiz, quiz_questions=quiz_ques)





@app.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
def submit_quiz(quiz_id):
    user_email = session.get('user_email')
    quiz = quizs.query.get_or_404(quiz_id)
    quiz_questions = questions.query.filter_by(quiz_id=quiz.id).all()

    marks = 0
    attempted = 0
    total_questions = len(quiz_questions)

    for question in quiz_questions:
        user_answer = request.form.get(f'answer_{question.id}')
        
        if user_answer:
            attempted += 1  # Count attempted questions
            
            # Match user-selected answer to its option number
            correct_option_number = None
            for i, option in enumerate([question.option1, question.option2, question.option3, question.option4], start=1):
                if user_answer.strip() == option.strip():  # Match text
                    correct_option_number = f"option{i}"
                    break

            # Now compare with stored correct answer
            if correct_option_number and correct_option_number == question.answer.strip().lower():
                marks += 1
    score = round((marks / total_questions * 100) if total_questions else 0)

    # Store result without percentage conversion
    new_score = Score(
        user_email=user_email,  
        quiz_id=quiz_id,
        score=score,
        total_questions=total_questions,
        timestamp=datetime.utcnow()
    )
    db.session.add(new_score)
    db.session.commit()

    flash('Quiz submitted!')
    return redirect(url_for('home'))
 

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "GET":
        return render_template('search.html')
    
    if request.method == "POST":
        search_term = request.form.get('search', None)

        # Search across subjects, chapters, and quizzes
        search_subjects = subjects.query.filter(subjects.name.ilike(f'%{search_term}%')).all()
        search_chapters = chapters.query.filter(chapters.name.ilike(f'%{search_term}%')).all()
        search_quizzes = quizs.query.filter(quizs.name.ilike(f'%{search_term}%')).all()

        return render_template('search.html', search_subjects=search_subjects, search_chapters=search_chapters, search_quizzes=search_quizzes, search_term=search_term)





@app.route('/about')
def about():
    return render_template('about.html')