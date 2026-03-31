from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
app = Flask(__name__)

@app.route("/")
def SignInPage():
    return render_template("SignInPage.html")

@app.route("/home")
def HomePage():
    return render_template("HomePage.html")

@app.route("/resources")
def Resources():
    return render_template("Resources.html")

@app.route("/registration", methods=['GET','POST'])
def Register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        year_level = request.form['year_level']
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('db//akoconnect.db')  
        cursor = conn.cursor()
        # cursor.execute('SELECT * FROM "User"')
        # existing_user = cursor.fetchone()
        # if existing_user:
        #     conn.close()
        ##Inserting a new user
        cursor.execute("INSERT INTO User (full_name, email, year_level, username, password) VALUES (?, ?, ?, ?, ?)", (full_name, email, year_level, username, password))
        conn.commit()
        conn.close()
        return redirect(url_for("Login"))
    else:
        return render_template("Registration.html")
        


@app.route('/login', methods=['GET','POST']) ##login
def Login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')


        conn = sqlite3.connect('db//akoconnect.db')  
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM User WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()


        conn.close()

        if user:
            return redirect (url_for('HomePage'))
        else:
            return "Invalid Username or Password."
    else:
        return render_template ("SignInPage.html")

@app.route('/tutorbooking')
def GetTutor():  
    # 1. Go to the DB and say "Give me the info for ID #"
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, bio FROM tutors WHERE id = ?", (tutor_id,))
    data = cursor.fetchone() # This gets the specific row
    conn.close()
    # 2. Send that SPECIFIC data to the SAME page template
    return render_template('HomePage.html', name=data[0], bio=data[1])



if __name__ == "__main__":
    app.run(debug=True)