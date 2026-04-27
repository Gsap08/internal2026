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

@app.route('/tutorpage')
def TutorPage():
    return render_template ("TutorPage.html", tutor_info=None)

@app.route('/bookingpage')
def BookingPage():
    tutor = request.args.get("choice")
    if not tutor:
        return redirect(url_for("TutorPage"))

    extra_map = {
        "1": "This tutor is good for beginners.",
        "2": "This tutor is very advanced."
    }

    extra_info = extra_map.get(tutor, "")

    conn = sqlite3.connect('db//akoconnect.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM Tutors WHERE tutor_id = ?",
        (int(tutor),)
    )

    tutor_info = cursor.fetchone()
    conn.close()

    return render_template(
        "BookingPage.html",
        tutor_info=tutor_info,
        extra_info=extra_info
    )



if __name__ == "__main__":
    app.run(debug=True)