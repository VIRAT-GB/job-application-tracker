from datetime import datetime, date
import os

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from flask_sqlalchemy import SQLAlchemy

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import generate_password_hash, check_password_hash


# ---------------------------------------------------------
# FLASK APPLICATION SETUP
# ---------------------------------------------------------

app = Flask(__name__)

# Use an environment variable for the secret key.
# The fallback is only for local development.
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY',
    'development-secret-key'
)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydata.db'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


# ---------------------------------------------------------
# APPLICATION STATUSES
# ---------------------------------------------------------

VALID_STATUSES = [
    'Applied',
    'Interview',
    'Offer',
    'Rejected'
]


# ---------------------------------------------------------
# USER MODEL
# ---------------------------------------------------------

class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    def set_password(self, password):
        # Store a secure hash instead of the actual password.
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # Compare the entered password with the stored hash.
        return check_password_hash(
            self.password_hash,
            password
        )


# ---------------------------------------------------------
# JOB APPLICATION MODEL
# ---------------------------------------------------------

class Application(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    company = db.Column(
        db.String(120),
        nullable=False
    )

    role = db.Column(
        db.String(120),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default='Applied'
    )

    date_applied = db.Column(
        db.Date,
        nullable=False,
        default=date.today
    )

    notes = db.Column(
        db.Text
    )

    def to_dict(self):

        return {
            'id': self.id,
            'company': self.company,
            'role': self.role,
            'status': self.status,
            'date_applied': self.date_applied.strftime('%Y-%m-%d'),
            'notes': self.notes or ''
        }


# ---------------------------------------------------------
# FLASK-LOGIN USER LOADER
# ---------------------------------------------------------

@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        User,
        int(user_id)
    )


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------

@app.route('/')
def home():

    return render_template(
        'home.html',
        name='Virat'
    )


# ---------------------------------------------------------
# SIGN UP
# ---------------------------------------------------------

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        name = request.form.get(
            'name',
            ''
        ).strip()

        email = request.form.get(
            'email',
            ''
        ).strip().lower()

        password = request.form.get(
            'password',
            ''
        )

        # Check required fields.
        if not name or not email or not password:

            return render_template(
                'signup.html',
                error='All fields are required.'
            )

        # Check minimum password length.
        if len(password) < 6:

            return render_template(
                'signup.html',
                error='Password must be at least 6 characters.'
            )

        # Check whether the email already exists.
        if User.query.filter_by(
            email=email
        ).first():

            return render_template(
                'signup.html',
                error='This email is already registered.'
            )

        # Create a new user.
        new_user = User(
            name=name,
            email=email
        )

        # Hash the password.
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash(
            'Account created! Please log in.'
        )

        return redirect(
            url_for('login')
        )

    return render_template(
        'signup.html'
    )


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get(
            'email',
            ''
        ).strip().lower()

        password = request.form.get(
            'password',
            ''
        )

        # Find the user using their email.
        user = User.query.filter_by(
            email=email
        ).first()

        # Validate login credentials.
        if not user or not user.check_password(password):

            return render_template(
                'login.html',
                error='Invalid email or password.'
            )

        # Create the user's login session.
        login_user(user)

        return redirect(
            url_for('dashboard')
        )

    return render_template(
        'login.html'
    )


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------

@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(
        url_for('login')
    )


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard():

    return render_template(
        'dashboard.html',
        statuses=VALID_STATUSES
    )


# =========================================================
# REST API — APPLICATIONS
# =========================================================


# ---------------------------------------------------------
# GET APPLICATIONS
# ---------------------------------------------------------

@app.route('/api/applications', methods=['GET'])
@login_required
def api_get_applications():

    # Only get applications belonging to the logged-in user.
    query = Application.query.filter_by(
        user_id=current_user.id
    )

    # Get selected status filter.
    status = request.args.get(
        'status',
        'All'
    )

    if status in VALID_STATUSES:

        query = query.filter_by(
            status=status
        )

    # Get search text.
    search = request.args.get(
        'search',
        ''
    ).strip()

    if search:

        query = query.filter(
            Application.company.ilike(
                f'%{search}%'
            )
        )

    # Get sorting option.
    sort = request.args.get(
        'sort',
        'newest'
    )

    if sort == 'oldest':

        query = query.order_by(
            Application.date_applied.asc()
        )

    else:

        query = query.order_by(
            Application.date_applied.desc()
        )

    applications = query.all()

    return jsonify([
        application.to_dict()
        for application in applications
    ])


# ---------------------------------------------------------
# CREATE APPLICATION
# ---------------------------------------------------------

@app.route('/api/applications', methods=['POST'])
@login_required
def api_create_application():

    data = request.get_json()

    # Check that JSON data was received.
    if not data:

        return jsonify({
            'error': 'Invalid request data.'
        }), 400

    company = (
        data.get('company') or ''
    ).strip()

    role = (
        data.get('role') or ''
    ).strip()

    status = data.get(
        'status',
        'Applied'
    )

    date_str = data.get(
        'date_applied',
        ''
    )

    notes = (
        data.get('notes') or ''
    ).strip()

    # Validate company and role.
    if not company or not role:

        return jsonify({
            'error': 'Company and role are required.'
        }), 400

    # Validate application status.
    if status not in VALID_STATUSES:

        return jsonify({
            'error': 'Invalid status.'
        }), 400

    # Convert the date from string to Python date.
    try:

        date_applied = (
            datetime.strptime(
                date_str,
                '%Y-%m-%d'
            ).date()
            if date_str
            else date.today()
        )

    except ValueError:

        return jsonify({
            'error': 'Invalid date format.'
        }), 400

    # Create the application.
    new_application = Application(
        user_id=current_user.id,
        company=company,
        role=role,
        status=status,
        date_applied=date_applied,
        notes=notes
    )

    db.session.add(new_application)
    db.session.commit()

    return jsonify(
        new_application.to_dict()
    ), 201


# ---------------------------------------------------------
# UPDATE APPLICATION
# ---------------------------------------------------------

@app.route(
    '/api/applications/<int:app_id>',
    methods=['PUT']
)
@login_required
def api_update_application(app_id):

    application = db.get_or_404(
        Application,
        app_id
    )

    # Make sure the logged-in user owns this application.
    if application.user_id != current_user.id:

        return jsonify({
            'error': 'Not authorized.'
        }), 403

    data = request.get_json()

    if not data:

        return jsonify({
            'error': 'Invalid request data.'
        }), 400

    # Update status.
    if 'status' in data:

        if data['status'] not in VALID_STATUSES:

            return jsonify({
                'error': 'Invalid status.'
            }), 400

        application.status = data['status']

    # Update company.
    if 'company' in data:

        application.company = (
            data['company'] or ''
        ).strip()

    # Update role.
    if 'role' in data:

        application.role = (
            data['role'] or ''
        ).strip()

    # Update notes.
    if 'notes' in data:

        application.notes = (
            data['notes'] or ''
        ).strip()

    db.session.commit()

    return jsonify(
        application.to_dict()
    )


# ---------------------------------------------------------
# DELETE APPLICATION
# ---------------------------------------------------------

@app.route(
    '/api/applications/<int:app_id>',
    methods=['DELETE']
)
@login_required
def api_delete_application(app_id):

    application = db.get_or_404(
        Application,
        app_id
    )

    # Make sure the logged-in user owns this application.
    if application.user_id != current_user.id:

        return jsonify({
            'error': 'Not authorized.'
        }), 403

    db.session.delete(application)
    db.session.commit()

    return jsonify({
        'message': 'Deleted.'
    })


# ---------------------------------------------------------
# APPLICATION STATISTICS
# ---------------------------------------------------------

@app.route('/api/stats')
@login_required
def api_stats():

    # Start each status counter at zero.
    stats = {
        status: 0
        for status in VALID_STATUSES
    }

    # Get only this user's applications.
    applications = Application.query.filter_by(
        user_id=current_user.id
    ).all()

    # Count applications by status.
    for application in applications:

        if application.status in stats:

            stats[application.status] += 1

    # Calculate total applications.
    stats['Total'] = len(
        applications
    )

    return jsonify(stats)


# ---------------------------------------------------------
# CREATE DATABASE TABLES
# ---------------------------------------------------------

with app.app_context():

    db.create_all()


# ---------------------------------------------------------
# START FLASK APPLICATION
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5001
    )