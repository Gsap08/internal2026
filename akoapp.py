from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, os
import bcrypt
from datetime import datetime, timedelta
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

        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        conn = sqlite3.connect('db//akoconnect.db')  
        cursor = conn.cursor()
        cursor.execute("INSERT INTO User (full_name, email, year_level, username, password) VALUES (?, ?, ?, ?, ?)", (full_name, email, year_level, username, hashed_password))
        conn.commit()
        conn.close()
        return redirect(url_for("Login"))
    else:
        return render_template("Registration.html")
        


@app.route('/login', methods=['GET','POST'])
def Login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('db//akoconnect.db')
        cursor = conn.cursor()

        # Find user by username
        cursor.execute(
            "SELECT * FROM User WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        if user:
            stored_hash = user[4]

            # Compare entered password against stored hash
            if bcrypt.checkpw(
                password.encode('utf-8'),
                stored_hash.encode('utf-8')
            ):
                session['role'] = user[6]
                session['user_id'] = user[0]

                conn.close()
                return redirect(url_for('HomePage'))

        conn.close()
        return render_template(
            "SignInPage.html",
            error="Incorrect Username or Password."
        )

    return render_template("SignInPage.html")

@app.route('/tutorpage')
def TutorPage():
    return render_template ("TutorPage.html", tutor_info=None)


@app.route('/bookingpage')
def BookingPage():
    tutor = request.args.get("choice")

    if tutor:
        session['tutor_id'] = tutor
        tutor_id = int(tutor)
    else:
        tutor_id = session.get('tutor_id')

    if not tutor_id:
        return redirect(url_for("TutorPage"))

    conn = sqlite3.connect('db//akoconnect.db')
    cursor = conn.cursor()
    cursor.execute("SELECT tutor_id, full_name, year_level, email, subject_options, user_id FROM Tutors WHERE tutor_id = ?",(tutor,))
    tutor_info = cursor.fetchone()
    cursor.execute('SELECT tutor_image FROM Tutors where tutor_id =?', (tutor_id,))
    tutor_image = cursor.fetchone()
    tutor_image = tutor_image[0]
    cursor.execute("SELECT timeslot_id, day, session_time FROM Tutor_Timeslot WHERE tutor_id = ?", ((tutor_id,)))
    timeslots = cursor.fetchall()
    cursor.execute("SELECT subject FROM Subjects WHERE tutor_id = ?", (tutor_id,))
    subjects = cursor.fetchall()
    cursor.execute("SELECT DISTINCT day FROM Tutor_Timeslot WHERE tutor_id = ?", ((tutor_id,)))
    available_days = cursor.fetchall()

#convert database result into list 
    allowed_days = [d[0] for d in available_days]

    day_map = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6
    }

    allowed_numbers = [day_map[d] for d in allowed_days]

    available_dates = []

    today = datetime.today()

    for i in range(30):
        day = today + timedelta(days=i)

        if day.weekday() in allowed_numbers:
            available_dates.append({
                "value": day.strftime("%Y-%m-%d"),
                "label": day.strftime("%A, %d %B %Y")
            })

    conn.close()
    return render_template ("BookingPage.html",tutor_image=tutor_image, tutor_info=tutor_info, timeslots=timeslots, subjects=subjects, available_dates=available_dates)

@app.route('/confirmationpage', methods=['POST'])
def SaveBooking():
    tutor = int(session.get('tutor_id'))
    booked_timeslot = request.form.get('timeslot')
    booked_subject = request.form.get('subject')
    booked_date = request.form.get('session_date')
    user_id = session.get('user_id')

    conn = sqlite3.connect('db//akoconnect.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO Bookings (tutor_id, user_id, booked_timeslot, booked_subject, booked_date) VALUES (?,?,?,?,?)", (tutor, user_id, booked_timeslot, booked_subject, booked_date))
    
    booking_id = cursor.lastrowid
    cursor.execute(" SELECT Bookings.booking_id, Tutors.full_name, Bookings.booked_timeslot, Bookings.booked_subject, Bookings.booked_date FROM Bookings JOIN Tutors ON Bookings.tutor_id = Tutors.tutor_id WHERE Bookings.booking_id = ?", (booking_id,))

    booking = cursor.fetchone()
    conn.commit()
    conn.close()

    
    return render_template ("ConfirmationPage.html", booking=booking)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('Login'))

@app.route ('/bookings')
def BookingInfo():
    tutor_bookings = [] #Necessary tutor_bookings will not exist otherwise, and will crash later.
    conn = sqlite3.connect('db//akoconnect.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    user_id = session.get('user_id')
    role = session.get('role')

    cursor.execute(
        """
        SELECT 
        Bookings.tutor_id, 
        Bookings.booking_id,
        Bookings.booked_timeslot AS timeslot, 
        Bookings.booked_subject AS subject, 
        Bookings.booked_date AS date,
        Tutors.full_name AS tutor_name 
        FROM Bookings 
        JOIN Tutors on Bookings.tutor_id = Tutors.tutor_id 
        where Bookings.user_id = ?""", (user_id,))
        
    book_info = cursor.fetchall()

    if role == 'tutor':
        cursor.execute("SELECT tutor_id FROM Tutors where user_id =?", (user_id,))
        tutor = cursor.fetchone()
        if tutor:
            tutor = tutor["tutor_id"]
            cursor.execute("""
                    SELECT
                    Bookings.booking_id,
                    Bookings.booked_subject AS subject,
                    Bookings.booked_timeslot AS timeslot,
                    Bookings.booked_date AS date,
                    User.full_name AS student_name
                    FROM Bookings
                    JOIN User ON Bookings.user_id = User.user_id
                    WHERE Bookings.tutor_id = ?
                """, (tutor,))
            tutor_bookings = cursor.fetchall()
    # convert date for display
    formatted = []
    for b in book_info:
        date_obj = datetime.strptime(b["date"], "%Y-%m-%d")
        b = dict(b)
        b["date_display"] = date_obj.strftime("%A, %d %B %Y")
        formatted.append(b)
    conn.close()
    return render_template("BookingInfo.html", book_info=formatted, role=role, tutor_bookings=tutor_bookings)


@app.route('/delete_booking/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    conn = sqlite3.connect('db//akoconnect.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Bookings where booking_id = ?', (booking_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('BookingInfo'))
if __name__ == "__main__":
    app.run(debug=True)