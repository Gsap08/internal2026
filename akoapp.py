from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, os
app = Flask(__name__)
app.secret_key = os.urandom(24)

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
        session['user_id'] = user[0]

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
    session['tutor_id'] = tutor
    if not tutor:
        return redirect(url_for("TutorPage"))

    #Dictionary for extra information
    extra_map = {
        "1": "This tutor is good for beginners.",
        "2": "This tutor is very advanced."
    }
    extra_info = extra_map.get(tutor, "")
    conn = sqlite3.connect('db//akoconnect.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Tutors WHERE tutor_id = ?",(int(tutor),))
    tutor_info = cursor.fetchone()
    cursor.execute("SELECT timeslot_id, day, session_time FROM Tutor_Timeslot WHERE tutor_id = ?", (int(tutor),))
    timeslots = cursor.fetchall()
    cursor.execute("SELECT subject FROM Subjects WHERE tutor_id = ?", (tutor,))
    subjects = cursor.fetchall()

    conn.close()
    return render_template ("BookingPage.html",tutor_info=tutor_info,extra_info=extra_info, timeslots=timeslots, subjects=subjects)

@app.route('/confirmationpage', methods=['POST'])
def SaveBooking():
    tutor = int(session.get('tutor_id'))
    booked_timeslot = request.form.get('timeslot')
    booked_subject = request.form.get('subject')
    user_id = session.get('user_id')

    conn = sqlite3.connect('db//akoconnect.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO Bookings (tutor_id, user_id, booked_timeslot, booked_subject) VALUES (?,?,?,?)", (tutor, user_id, booked_timeslot, booked_subject,))
    
    booking_id = cursor.lastrowid
    cursor.execute(" SELECT Bookings.booking_id, Tutors.full_name, Bookings.booked_timeslot, Bookings.booked_subject FROM Bookings JOIN Tutors ON Bookings.tutor_id = Tutors.tutor_id WHERE Bookings.booking_id = ?", (booking_id,))

    booking = cursor.fetchone()
    conn.commit()
    conn.close()

    
    return render_template ("ConfirmationPage.html", booking=booking)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('Login'))

@app.route ('/dashboard')
def Dashboard():
    conn = sqlite3.connect('db//akoconnect.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    user_id = session.get('user_id')
    cursor.execute(
        """
        SELECT Bookings.tutor_id, 
        Bookings.booked_timeslot AS timeslot, 
        Bookings.booked_subject AS subject, 
        Tutors.full_name AS tutor_name 
        FROM Bookings 
        JOIN Tutors on Bookings.tutor_id = Tutors.tutor_id 
        where Bookings.user_id = ?""", (user_id,))
        
    dash_info = cursor.fetchall()
    conn.commit()
    conn.close()
    
    return render_template("Dashboard.html", dash_info=dash_info)

if __name__ == "__main__":
    app.run(debug=True)