from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from pymongo import MongoClient
from bson import ObjectId
import os
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secure secret key

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['quiz_database']
users = db['users']
quiz_collection = db['quiz_collection']
results_collection = db['results_collection']  # Collection for storing results

# Directory to store PDF files
PDF_DIRECTORY = 'pdfs'

# Home route redirects to login page
@app.route('/')
def home():
    return redirect(url_for('login'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.find_one({'email': email})
        
        if user:
            # Verify the password (as plain text)
            if password == user['password']:
                session['email'] = user['email']
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials, try again.')
        else:
            flash('User not found.')
    
    return render_template('login.html')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if users.find_one({'email': email}):
            flash('User already exists.')
            return redirect(url_for('signup'))
        
        # Store plain text password (NOT SECURE, just for demonstration)
        users.insert_one({
            'username': username,
            'email': email,
            'password': password  # Store password as plain text
        })
        
        flash('Signup successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'email' in session:  # Check if user is logged in
        return render_template('index.html')
    else:
        flash('Please login first.')
        return redirect(url_for('login'))

# Logout route to clear the session
@app.route('/logout')
def logout():
    session.pop('email', None)  # Remove email from session
    flash('You have been logged out.')
    return redirect(url_for('login'))

# Materials route
@app.route('/materials')
def materials():
    if 'email' in session:  # Check if user is logged in
        return render_template('materials.html')
    else:
        flash('Please login first.')
        return redirect(url_for('login'))
    
# Data Science PDF route
@app.route('/materials/data-science')
def data_science_pdf():
    if 'email' in session:  # Check if user is logged in
        pdf_path = os.path.join(PDF_DIRECTORY, 'data_science.pdf')
        return send_file(pdf_path, as_attachment=False, mimetype='application/pdf')
    else:
        flash('Please login first.')
        return redirect(url_for('login'))
    # Data Science PDF route (generalized for multiple subjects)
@app.route('/materials/<pdf_name>')
def serve_pdf(pdf_name):
    if 'email' in session:
        pdf_path = os.path.join(PDF_DIRECTORY, pdf_name)
        
        if not os.path.exists(pdf_path):
            flash('PDF not found.')
            return redirect(url_for('materials'))
        
        return send_file(pdf_path, as_attachment=False, mimetype='application/pdf')
    else:
        flash('Please login first.')
        return redirect(url_for('login'))

# PDF Viewer HTML route
@app.route('/view-pdf')
def view_pdf():
    if 'email' in session:  # Check if user is logged in
        pdf_name = request.args.get('pdf_name')  # Get the PDF name from URL parameters
        return render_template('pdf_viewer.html', pdf_name=pdf_name)
    else:
        flash('Please login first.')
        return redirect(url_for('login'))

# Years route
@app.route('/years')
def years():
    if 'email' in session:  # Check if user is logged in
        return render_template('years.html')
    else:
        flash('Please login first.')
        return redirect(url_for('login'))

@app.route('/1st_year')
def first_year():
    if 'email' in session:
        return render_template('1st_year.html')
    else:
        flash('Please login first.')
        return redirect(url_for('login'))

# 2nd Year route
@app.route('/2nd_year')
def second_year():
    if 'email' in session:
        return render_template('2nd_year.html')
    else:
        flash('Please login first.')
        return redirect(url_for('login'))

@app.route('/3rd_year')
def third_year():
    if 'email' in session:
        return render_template('3rd_year.html')
    else:
        flash('Please login first.')
        return redirect(url_for('login'))

# 4th Year route
@app.route('/4th_year')
def fourth_year():
    if 'email' in session:
        return render_template('4th_year.html')
    else:
        flash('Please login first.')
        return redirect(url_for('login'))

@app.route('/quiz/<subject>')
def load_quiz(subject):
    if 'email' in session:  # Check if user is logged in
        subject = subject.capitalize()
        quiz = list(quiz_collection.find({"subject": subject}))
        
        if not quiz:
            return f"No quiz available for {subject}."
        
        return render_template('quiz.html', quiz=quiz, subject=subject)
    else:
        flash('Please login first.')
        return redirect(url_for('login'))


# Route to handle quiz submission
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    # Ensure the user is logged in
    if 'email' in session:
        # Extract student details
        student_details = {
            'name': request.form['name'],
            'rollno': request.form['rollno'],
            'branch': request.form['branch'],
            'section': request.form['section']
        }

        # Extract quiz answers
        answers = {k: v for k, v in request.form.items() if k.startswith('q')}

        # Initialize score
        score = 0

        # Loop through each answer
        for question_id, selected_option in answers.items():
            # Extract actual MongoDB ID by removing the 'q' prefix
            question_id = question_id[1:]  # Remove the 'q'
            
            # Retrieve question from MongoDB by its _id, which is an ObjectId
            question = quiz_collection.find_one({'_id': ObjectId(question_id)})
            
            # Check if the selected answer matches the correct answer
            if question and question['answer'] == selected_option:
                score += 1

        # Save results to MongoDB
        result = {
            'student_details': student_details,
            'score': score
        }
        results_collection.insert_one(result)
        
        # Redirect to home page after submission
        return redirect(url_for('home'))

    # If user is not logged in, redirect to login page
    else:
        flash('Please login first.')
        return redirect(url_for('login'))


# Ensure the PDF directory exists (if you're using it)
PDF_DIRECTORY = './pdfs'  # Set the correct path
if not os.path.exists(PDF_DIRECTORY):
    os.makedirs(PDF_DIRECTORY)

if __name__ == '__main__':
    app.run(debug=True)