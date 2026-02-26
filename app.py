from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)

@app.route("/")
def signinpage():
    return render_template("SignInPage.html")

@app.route("/home")
def HomePage():
    return render_template("HomePage.html")

@app.route("/resources")
def Resources():
    return render_template("Resources.html")

if __name__ == "__main__":
    app.run(debug=True)