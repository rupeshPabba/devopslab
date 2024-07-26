from flask import Flask, render_template, request, redirect, url_for
import re
import smtplib
import random
import string
import mysql.connector
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)


def create_table():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="mysql123",
        database="devops"
    )
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INT PRIMARY KEY AUTO_INCREMENT,
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        username VARCHAR(255),
        email VARCHAR(255),
        password VARCHAR(255),
        dob DATE,
        otp VARCHAR(255)
    )''')
    conn.commit()
    conn.close()


def register_user(first_name, last_name, username, email, password, dob):
    otp = generate_otp()

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="mysql123",
        database="devops"
    )

    cursor = conn.cursor()

    insert_query = "INSERT INTO users (first_name, last_name, username, email, password, dob, otp) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    insert_data = (first_name, last_name, username, email, password, dob, otp)

    cursor.execute(insert_query, insert_data)

    conn.commit()
    conn.close()

    send_otp_email(email, otp)


def generate_otp(length=4):
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(email, otp):
    smtp_host = 'smtp-mail.outlook.com'
    smtp_port = 587
    sender_email = 'ashwinrajlendalay@outlook.com'
    sender_password = '1Rockmyself!'

    subject = 'OTP for Registration'
    message = f'Your OTP is: {otp}'

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())


NAME_REGEX = re.compile(r"^[a-zA-Z]+(?:\s+[a-zA-Z]+)*$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{6,}$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%?&0-9])[A-Za-z\d@$!%?&]{8,}$")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    create_table()

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    dob = request.form['dob']

    if not NAME_REGEX.match(first_name):
        return "Invalid first name"

    if not NAME_REGEX.match(last_name):
        return "Invalid last name"

    if not USERNAME_REGEX.match(username):
        return "Invalid username"

    if not EMAIL_REGEX.match(email):
        return "Invalid email"

    if not PASSWORD_REGEX.match(password):
        return "Invalid password"

    try:
        register_user(first_name, last_name, username, email, password, dob)
        return redirect(url_for('verify_otp', username=username))
    except mysql.connector.Error as error:
        return f"Error while registering: {str(error)}"


@app.route('/verify_otp/<username>', methods=['GET', 'POST'])
def verify_otp(username):
    if request.method == 'GET':
        return render_template('otp.html', username=username)

    otp = request.form['otp']

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql123",
            database="devops"
        )
        cursor = conn.cursor()

        select_query = "SELECT otp FROM users WHERE username = %s"
        select_data = (username,)

        cursor.execute(select_query, select_data)

        result = cursor.fetchone()

        if result and result[0] == otp:
            update_query = "UPDATE users SET otp = NULL WHERE username = %s"
            update_data = (username,)

            cursor.execute(update_query, update_data)

            conn.commit()
            conn.close()
            return redirect(url_for('signin', username=username))

        return "Invalid OTP"
    except mysql.connector.Error as error:
        return f"Error while verifying OTP: {str(error)}"


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        return render_template('signin.html')

    username = request.form['username']
    password = request.form['password']

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql123",
            database="devops"
        )
        cursor = conn.cursor()

        select_query = "SELECT username, password FROM users WHERE username = %s"
        select_data = (username,)

        cursor.execute(select_query, select_data)

        result = cursor.fetchone()

        if result and result[0] == username and result[1] == password:
            conn.close()
            return redirect(url_for('e_com', username=username))

        return "Invalid username or password"
    except mysql.connector.Error as error:
        return f"Error while signing in: {str(error)}"


@app.route('/e_com/<username>')
def e_com(username):
    items = [
        {'name': 'kiwi', 'price': 10},
        {'name': 'iphine', 'price': 20},
        {'name': 'jack', 'price': 30},
        {'name': 'paya', 'price': 40},
        {'name': 'bones', 'price': 50}
    ]
    return render_template('e_com.html', username=username, items=items)


if __name__ == '__main__':
    app.run(debug=True)
