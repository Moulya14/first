from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy data for shifts and employees
shifts = [
    {'type': 'Fixed', 'start': '09:00', 'end': '17:00', 'break': '60'},
    {'type': 'Flexible', 'start': '10:00', 'end': '18:00', 'break': '30'},
]

employees = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'emp1': {'password': 'pass123', 'role': 'employee'}
}

assignments = {}   # Store shift assignments

# Index page (Login page)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = employees.get(username)

        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('admin_dashboard' if user['role'] == 'admin' else 'employee_dashboard'))
        else:
            return 'Invalid login credentials, please try again.'

    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        if username in employees:
            return render_template('register.html', error_message='User already exists!')

        employees[username] = {'password': password, 'role': user_type}
        return render_template('register.html', success_message='User registered successfully!')

    return render_template('register.html')



# Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))

    return render_template('admin_dashboard.html', shifts=shifts)

# Define New Shift
@app.route('/define_shift', methods=['GET', 'POST'])
def define_shift():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))

    if request.method == 'POST':
        shift_type = request.form['shift_type']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        break_duration = request.form['break_duration']
        
        shifts.append({
            'type': shift_type,
            'start': start_time,
            'end': end_time,
            'break': break_duration
        })
        
        return redirect(url_for('admin_dashboard'))

    return render_template('define_shift.html', shifts=shifts)

# Assign Shift to Employee
@app.route('/assign_shift', methods=['GET', 'POST'])
def assign_shift():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))

    if request.method == 'POST':
        employee_id = request.form['employee_id']
        shift_id = int(request.form['shift_id']) - 1  # Adjust for 0-based index
        assignment_date = request.form['assignment_date']

        shift = shifts[shift_id]

        if employee_id not in assignments:
            assignments[employee_id] = []

        assignments[employee_id].append({
            'shift': shift,
            'date': assignment_date
        })

        return redirect(url_for('admin_dashboard'))

    return render_template('assign_shift.html', employees=employees.keys(), shifts=shifts)


# Employee Dashboard
@app.route('/employee_dashboard')
def employee_dashboard():
    if 'username' not in session or session['role'] != 'employee':
        return redirect(url_for('index'))

    # Record attendance for the employee
    username = session['username']
    
    return render_template('employee_dashboard.html', shifts=shifts, attendance="Attendance details here")

# View Attendance (Admin only)
@app.route('/view_attendance')
def view_attendance():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))

    return render_template('view_attendance.html', assignments=assignments)



# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
