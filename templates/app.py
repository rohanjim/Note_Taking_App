from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key in production

# Database connection function
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='note_taking_db',
            user='root',
            password='Rohan@123'
        )
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None

# Home page route
@app.route('/')
def home():
    return render_template('home.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Registration successful! Please log in.', 'success')
        return redirect('/login')

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        cursor.fetchall()  # clear remaining result
        cursor.close()
        conn.close()

        if user:
            session['user_id'] = user['id']
            flash('Logged in successfully!', 'success')
            return redirect('/notes')
        else:
            flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')

# Notes route
@app.route('/notes', methods=['GET', 'POST'])
def notes():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        note_content = request.form['note']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO notes (user_id, content) VALUES (%s, %s)', (session['user_id'], note_content))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Note added!', 'success')
        return redirect('/notes')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM notes WHERE user_id = %s', (session['user_id'],))
    notes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('notes.html', notes=notes)

# Delete note route
@app.route('/delete_note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notes WHERE id = %s AND user_id = %s', (note_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Note deleted successfully!', 'success')

    return redirect('/notes')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
