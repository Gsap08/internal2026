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

        conn = sqlite3.connect('db\\akoconnect.db')  
        cursor = conn.cursor()
        # cursor.execute('SELECT * FROM "User"')
        # existing_user = cursor.fetchone()
        # if existing_user:
        #     conn.close()
        ##Inserting a new user
        cursor.execute("INSERT INTO User (full_name, email, year_level, username, password) VALUES (?, ?, ?, ?, ?)", (full_name, password, year_level, username, password ))
        conn.commit()
        conn.close()
        return redirect('{{url_for("Login")}}')
    else:
        return render_template("Registration.html")
        
    



@app.route('/login', methods=['POST']) ##login
def Login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('akoconnect.db')  
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()


    conn.close()

    if user:
        return render_template ("HomePage.html")
    else:
        return "Invalid Username or Password."

if __name__ == "__main__":
    app.run(debug=True)