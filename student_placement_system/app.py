from flask import Flask, render_template, request, redirect, url_for
from markupsafe import escape
import mysql.connector

app = Flask(__name__)

# =========================
# DATABASE SETTINGS
# =========================

DB_HOST = "localhost"
DB_USER = "placement_app"
DB_PASSWORD = "Place@12345"
DB_NAME = "placementmanagement"


def get_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


# =========================
# COMMON STYLE
# =========================

STYLE = """
<style>
body {
    font-family: Arial, sans-serif;
    background-color: #f4f7fb;
    margin: 0;
    padding: 40px;
}

h1 {
    color: #1f3c88;
    margin-bottom: 25px;
}

h2 {
    color: #333;
}

table {
    width: 90%;
    border-collapse: collapse;
    background-color: white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

th {
    background-color: #1f3c88;
    color: white;
    padding: 15px;
    text-align: left;
}

td {
    padding: 15px;
    border-bottom: 1px solid #ddd;
}

tr:hover {
    background-color: #f1f5ff;
}

form {
    background-color: white;
    padding: 25px;
    width: 350px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

label {
    display: block;
    margin-bottom: 6px;
    color: #1f3c88;
    font-weight: bold;
}

input {
    width: 100%;
    padding: 10px;
    margin-bottom: 18px;
    border: 1px solid #ccc;
    border-radius: 6px;
    box-sizing: border-box;
}

button {
    padding: 10px 20px;
    background-color: #1f3c88;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 15px;
}

button:hover {
    background-color: #162b63;
}

.btn {
    display: inline-block;
    margin-top: 20px;
    margin-right: 15px;
    padding: 10px 18px;
    background-color: #1f3c88;
    color: white;
    text-decoration: none;
    border-radius: 6px;
}

.btn:hover {
    background-color: #162b63;
}

.card {
    background: white;
    padding: 25px;
    width: 450px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
</style>
"""


def page(title, body):
    return (
        "<!DOCTYPE html>"
        "<html><head><title>" + title + "</title>"
        + STYLE +
        "</head><body>" + body + "</body></html>"
    )


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# STUDENT LOGIN
# =========================

@app.route("/student-login", methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        # Demo password
        if password != "student123":
            return page(
                "Login Failed",
                """
                <h1>Invalid Password</h1>
                <a class="btn" href="/student-login">Try Again</a>
                """
            )

        db = get_db()
        cursor = db.cursor(buffered=True)

        cursor.execute(
            """
            SELECT name, email, department, percentage, cgpa
            FROM students
            WHERE email = %s
            """,
            (email,)
        )

        student = cursor.fetchone()

        cursor.close()
        db.close()

        if student:

            return page(
                "Student Dashboard",
                """
                <h1>Student Dashboard</h1>

                <div class="card">
                    <h2>Welcome, """ + str(escape(student[0])) + """!</h2>

                    <p><b>Name:</b> """ + str(escape(student[0])) + """</p>
                    <p><b>Email:</b> """ + str(escape(student[1])) + """</p>
                    <p><b>Department:</b> """ + str(escape(student[2])) + """</p>
                    <p><b>Percentage:</b> """ + str(escape(student[3])) + """</p>
                    <p><b>CGPA:</b> """ + str(escape(student[4])) + """</p>
                </div>

                <a class="btn"
                   href="/student-placements?email=""" +
                str(escape(student[1])) +
                """">View Placement Opportunities</a>

                <a class="btn" href="/">Logout</a>
                """
            )

        else:
            return page(
                "Student Not Found",
                """
                <h1>Student details not found</h1>
                <p>Please contact the administrator.</p>
                <a class="btn" href="/student-login">Back to Login</a>
                """
            )

    return render_template("student_login.html")


# =========================
# ADMIN LOGIN
# =========================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        if email == "admin@gmail.com" and password == "admin123":
            return redirect(url_for("admin_dashboard"))

        return page(
            "Login Failed",
            """
            <h1>Invalid Email or Password</h1>
            <a class="btn" href="/admin-login">Try Again</a>
            """
        )

    return render_template("admin_login.html")


# =========================
# ADMIN DASHBOARD
# =========================

def dash_button(text, link, color):

    return (
        '<a href="' + link + '" '
        'style="display:block;width:250px;margin:12px auto;'
        'padding:15px 20px;background-color:' + color +
        ';color:white;text-decoration:none;border-radius:6px;">'
        + text + '</a>'
    )


@app.route("/admin-dashboard")
def admin_dashboard():

    return page(
        "Admin Dashboard",
        """
        <div style="text-align:center;">

        <h1>Admin Dashboard</h1>
        <h2>Welcome Admin!</h2>

        """ +
        dash_button("Add Student", "/add-student", "#3498db") +
        dash_button("View Students", "/view-students", "#2ecc71") +
        dash_button("Add Company", "/add-company", "#f1c40f") +
        dash_button("View Placements", "/view-placements", "#8e6bd1") +
        dash_button("View Applications", "/view-applications", "#e67e22") +
        dash_button("Logout", "/logout", "red") +

        """
        </div>
        """
    )


# =========================
# ADD STUDENT
# =========================

@app.route("/add-student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO students
            (name, email, percentage, department, cgpa)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                request.form["name"],
                request.form["email"],
                request.form["percentage"],
                request.form["department"],
                request.form["cgpa"]
            )
        )

        db.commit()

        cursor.close()
        db.close()

        return redirect(url_for("view_students"))

    return page(
        "Add Student",
        """
        <h1>Add Student</h1>

        <form method="POST">

            <label>Student Name</label>
            <input type="text" name="name" required>

            <label>Email</label>
            <input type="email" name="email" required>

            <label>Department</label>
            <input type="text" name="department" required>

            <label>Percentage</label>
            <input type="number" name="percentage" required>

            <label>CGPA</label>
            <input type="number" step="0.01" name="cgpa" required>

            <button type="submit">Add Student</button>

        </form>

        <a class="btn" href="/admin-dashboard">
            Back to Dashboard
        </a>
        """
    )


# =========================
# VIEW STUDENTS
# =========================

@app.route("/view-students")
def view_students():

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT name, email, department, percentage, cgpa
        FROM students
        ORDER BY cgpa DESC
        """
    )

    data = cursor.fetchall()

    cursor.close()
    db.close()

    rows = ""

    for name, email, department, percentage, cgpa in data:

        rows += (
            "<tr>"
            "<td>" + str(escape(name)) + "</td>"
            "<td>" + str(escape(email)) + "</td>"
            "<td>" + str(escape(department)) + "</td>"
            "<td>" + str(escape(percentage)) + "</td>"
            "<td>" + str(escape(cgpa)) + "</td>"
            "</tr>"
        )

    return page(
        "View Students",
        """
        <h1>Student List</h1>

        <table>
            <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Department</th>
                <th>Percentage</th>
                <th>CGPA</th>
            </tr>
        """ + rows + """
        </table>

        <a class="btn" href="/add-student">
            Add Another Student
        </a>

        <a class="btn" href="/admin-dashboard">
            Back to Dashboard
        </a>
        """
    )


# =========================
# ADD COMPANY
# =========================

@app.route("/add-company", methods=["GET", "POST"])
def add_company():

    if request.method == "POST":

        db = get_db()
        cursor = db.cursor()

        # IMPORTANT:
        # MySQL column is "company", NOT "company_name"

        cursor.execute(
            """
            INSERT INTO companies
            (company, job_role, package)
            VALUES (%s, %s, %s)
            """,
            (
                request.form["company"],
                request.form["job_role"],
                request.form["package"]
            )
        )

        db.commit()

        cursor.close()
        db.close()

        return redirect(url_for("view_placements"))

    return page(
        "Add Company",
        """
        <h1>Add Company</h1>

        <form method="POST">

            <label>Company Name</label>
            <input type="text" name="company" required>

            <label>Job Role</label>
            <input type="text" name="job_role" required>

            <label>Package</label>
            <input type="text" name="package" required>

            <button type="submit">Add Company</button>

        </form>

        <a class="btn" href="/admin-dashboard">
            Back to Dashboard
        </a>
        """
    )


# =========================
# VIEW PLACEMENTS
# =========================

@app.route("/view-placements")
def view_placements():

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT id, company, job_role, package
        FROM companies
        """
    )

    data = cursor.fetchall()

    cursor.close()
    db.close()

    rows = ""

    for company_id, company, job_role, package in data:

        rows += (
            "<tr>"
            "<td>" + str(escape(company)) + "</td>"
            "<td>" + str(escape(job_role)) + "</td>"
            "<td>" + str(escape(package)) + "</td>"
            "</tr>"
        )

    return page(
        "View Placements",
        """
        <h1>Placement Details</h1>

        <table>
            <tr>
                <th>Company</th>
                <th>Job Role</th>
                <th>Package</th>
            </tr>
        """ + rows + """
        </table>

        <a class="btn" href="/add-company">
            Add Another Company
        </a>

        <a class="btn" href="/admin-dashboard">
            Back to Dashboard
        </a>
        """
    )


# =========================
# STUDENT PLACEMENT OPPORTUNITIES
# =========================

@app.route("/student-placements")
def student_placements():

    student_email = request.args.get("email")

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT id, company, job_role, package
        FROM companies
        """
    )

    data = cursor.fetchall()

    cursor.close()
    db.close()

    rows = ""

    for company_id, company, job_role, package in data:

        rows += (
            "<tr>"
            "<td>" + str(escape(company)) + "</td>"
            "<td>" + str(escape(job_role)) + "</td>"
            "<td>" + str(escape(package)) + "</td>"
            "<td>"
            "<a class='btn' href='/apply/"
            + str(company_id)
            + "?email="
            + str(escape(student_email))
            + "'>Apply</a>"
            "</td>"
            "</tr>"
        )

    return page(
        "Placement Opportunities",
        """
        <h1>Placement Opportunities</h1>

        <table>
            <tr>
                <th>Company</th>
                <th>Job Role</th>
                <th>Package</th>
                <th>Action</th>
            </tr>
        """ + rows + """
        </table>

        <a class="btn" href="/student-login">
            Back to Login
        </a>
        """
    )


# =========================
# APPLY FOR PLACEMENT
# =========================

@app.route("/apply/<int:company_id>")
def apply(company_id):

    student_email = request.args.get("email")

    if not student_email:
        return page(
            "Error",
            """
            <h1>Student email missing</h1>
            <a class="btn" href="/student-login">Back</a>
            """
        )

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT company, job_role
        FROM companies
        WHERE id = %s
        """,
        (company_id,)
    )

    company_data = cursor.fetchone()

    if not company_data:
        cursor.close()
        db.close()

        return page(
            "Company Not Found",
            """
            <h1>Company not found</h1>
            <a class="btn" href="/student-login">Back</a>
            """
        )

    company = company_data[0]
    job_role = company_data[1]

    cursor.execute(
        """
        INSERT INTO applications
        (student_email, company, job_role, status)
        VALUES (%s, %s, %s, %s)
        """,
        (
            student_email,
            company,
            job_role,
            "Applied"
        )
    )

    db.commit()

    cursor.close()
    db.close()

    return page(
        "Application Submitted",
        """
        <h1>Application Submitted Successfully!</h1>

        <p><b>Student:</b> """ +
        str(escape(student_email)) +
        """</p>

        <p><b>Company:</b> """ +
        str(escape(company)) +
        """</p>

        <p><b>Job Role:</b> """ +
        str(escape(job_role)) +
        """</p>

        <a class="btn"
           href="/student-placements?email=""" +
        str(escape(student_email)) +
        """">
           Back to Placements
        </a>
        """
    )


# =========================
# ADMIN VIEW APPLICATIONS
# =========================

@app.route("/view-applications")
def view_applications():

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT student_email, company, job_role, status
        FROM applications
        ORDER BY id DESC
        """
    )

    data = cursor.fetchall()

    cursor.close()
    db.close()

    rows = ""

    for student_email, company, job_role, status in data:

        rows += (
            "<tr>"
            "<td>" + str(escape(student_email)) + "</td>"
            "<td>" + str(escape(company)) + "</td>"
            "<td>" + str(escape(job_role)) + "</td>"
            "<td>" + str(escape(status)) + "</td>"
            "</tr>"
        )

    return page(
        "View Applications",
        """
        <h1>Placement Applications</h1>

        <table>
            <tr>
                <th>Student Email</th>
                <th>Company</th>
                <th>Job Role</th>
                <th>Status</th>
            </tr>
        """ + rows + """
        </table>

        <a class="btn" href="/admin-dashboard">
            Back to Dashboard
        </a>
        """
    )


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    return page(
        "Logged Out",
        """
        <h1>You have been logged out!</h1>

        <a class="btn" href="/">
            Back to Home
        </a>
        """
    )


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)