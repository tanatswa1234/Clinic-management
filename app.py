from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management and flashing messages

# Database configuration
db_config = {
    'user': 'root',
    'password': 'Tanatswa23',
    'host': 'localhost',
    'database': 'uzclinic'
}

# Connect to MySQL database
def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Insert data into the users table
            cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
            connection.commit()

            flash('User signed up successfully!')
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Check if user exists
            cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()

            if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
                session['user'] = email  # Store user email in session
                flash('Login successful!')
                return redirect(url_for('menu'))  # Redirect to the menu page after login
            else:
                flash('Invalid email or password.')
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/menu')
def menu():
    if 'user' not in session:  # Check if user is logged in
        flash('Please log in to access the menu.')
        return redirect(url_for('login'))  # Redirect to login if not logged in

    return render_template('menu.html')  # Render the menu page

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/appointments', methods=['GET', 'POST'])
def appointments():
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        email = request.form['email']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']
        notes = request.form['notes']

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Insert appointment data into the appointments table
            cursor.execute("INSERT INTO appointments (patient_name, email, appointment_date, appointment_time, notes) VALUES (%s, %s, %s, %s, %s)",
                           (patient_name, email, appointment_date, appointment_time, notes))
            connection.commit()

            flash('Appointment booked successfully!')
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('menu'))  # Redirect to appointments page after submission

    return render_template('appointments.html')

@app.route('/register_patient', methods=['GET', 'POST'])
def register_patient():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        gender = request.form['gender']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Insert data into the patients table
            cursor.execute("""
                INSERT INTO patients (first_name, last_name, dob, gender, email, phone, address)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (first_name, last_name, dob, gender, email, phone, address))
            connection.commit()

            flash('Patient registered successfully!')
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('menu'))

    return render_template('register_patient.html')

def linear_search(patients, key, value):
    results = []
    for patient in patients:
        if str(patient[key]).lower() == value.lower():
            results.append(patient)
    return results

def binary_search(patients, key, value):
    low, high = 0, len(patients) - 1
    while low <= high:
        mid = (low + high) // 2
        if str(patients[mid][key]).lower() == value.lower():
            return [patients[mid]]
        elif str(patients[mid][key]).lower() < value.lower():
            low = mid + 1
        else:
            high = mid - 1
    return []

# Sorting algorithms
def bubble_sort(patients, key):
    n = len(patients)
    for i in range(n):
        for j in range(0, n - i - 1):
            if patients[j][key] > patients[j + 1][key]:
                patients[j], patients[j + 1] = patients[j + 1], patients[j]
    return patients

def insertion_sort(patients, key):
    for i in range(1, len(patients)):
        current = patients[i]
        j = i - 1
        while j >= 0 and current[key] < patients[j][key]:
            patients[j + 1] = patients[j]
            j -= 1
        patients[j + 1] = current
    return patients

# Searching algorithms
def linear_search(patients, key, value):
    results = []
    for patient in patients:
        if str(patient[key]).lower() == value.lower():
            results.append(patient)
    return results

def binary_search(patients, key, value):
    low, high = 0, len(patients) - 1
    while low <= high:
        mid = (low + high) // 2
        if str(patients[mid][key]).lower() == value.lower():
            return [patients[mid]]
        elif str(patients[mid][key]).lower() < value.lower():
            low = mid + 1
        else:
            high = mid - 1
    return []

@app.route('/view_data', methods=['GET', 'POST'])
def view_data():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()
    cursor.close()
    connection.close()

    if request.method == 'POST':
        sort_alg = request.form.get('sort_alg')
        search_alg = request.form.get('search_alg')
        search_value = request.form.get('search_value')
        sort_key = request.form.get('sort_key')
        search_key = request.form.get('search_key')

        # Sorting
        if sort_alg == 'bubble_sort':
            patients = bubble_sort(patients, sort_key)
        elif sort_alg == 'insertion_sort':
            patients = insertion_sort(patients, sort_key)

        # Searching
        if search_value:
            if search_alg == 'linear_search':
                patients = linear_search(patients, search_key, search_value)
            elif search_alg == 'binary_search':
                # Make sure the data is sorted before performing a binary search
                patients = insertion_sort(patients, search_key)
                patients = binary_search(patients, search_key, search_value)

    return render_template('view_data.html', patients=patients)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        # Insert the contact form data into the database
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute("INSERT INTO contact_us (name, email, subject, message) VALUES (%s, %s, %s, %s)", 
                           (name, email, subject, message))
            connection.commit()

            flash('Your message has been sent successfully!', 'success')
        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user from session
    flash('You have been logged out successfully.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
