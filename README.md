# JobTrack – Job Application Tracker

JobTrack is a full-stack web application that helps users manage and track their job applications from a single dashboard.

Users can create an account, securely log in, add job applications, update application status, search and filter applications, and view application statistics.

## Live Demo

https://job-application-tracker-cohi.onrender.com

## GitHub Repository

https://github.com/VIRAT-GB/job-application-tracker

## Features

- User registration and login
- Secure password hashing
- Protected dashboard
- Add job applications
- Edit job applications
- Delete job applications
- Track application status
- Search applications by company
- Filter applications by status
- Sort applications by application date
- Dashboard application statistics
- REST API endpoints
- User-specific data authorization
- SQLite database
- Responsive web interface

## Tech Stack

### Backend

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Gunicorn

### Frontend

- HTML5
- CSS3
- JavaScript

### Database

- SQLite

### Tools & Deployment

- Git
- GitHub
- Render

## Project Architecture

```text
Browser
   |
   v
HTML / CSS / JavaScript
   |
   v
Flask Application
   |
   +---- Authentication
   |
   +---- REST APIs
   |
   +---- Application Logic
   |
   v
SQLAlchemy ORM
   |
   v
SQLite Database

## Database Design

JobTrack uses SQLite as its database.

The application contains two main tables:

### User

Stores user account information.

- `id`
- `name`
- `email`
- `password_hash`

### Application

Stores job application information.

- `id`
- `user_id`
- `company`
- `role`
- `status`
- `date_applied`
- `notes`

Each user can have multiple job applications.

```text
User
 |
 | 1
 |
 |------< many
             |
             v
       Application


 ## REST API

### Get Applications

GET /api/applications

Returns the logged-in user's job applications.

Supports:
- Status filtering
- Company search
- Date sorting

Example:

/api/applications?status=Interview

### Create Application

POST /api/applications

Creates a new job application.

### Update Application

PUT /api/applications/<id>

Updates an existing job application.

### Delete Application

DELETE /api/applications/<id>

Deletes an existing job application.

### Get Statistics

GET /api/stats

Returns the user's application statistics by status.


## Authentication & Authorization

JobTrack uses Flask-Login for session-based authentication.

Passwords are securely hashed using Werkzeug before being stored in the database.

Protected routes require the user to be logged in.

The application also checks that the logged-in user owns an application before allowing it to be updated or deleted.

This prevents users from accessing or modifying another user's job application data.


## Running the Project Locally

Clone the repository:

```bash
git clone https://github.com/VIRAT-GB/job-application-tracker.git

## Deployment

JobTrack is deployed using Render.

The application uses Gunicorn as the production WSGI server.

Production start command:

gunicorn app:app

The source code is maintained on GitHub and deployed from the main branch.

## Future Improvements

- Job location tracking
- Job application URLs
- Pagination
- Email reminders
- Advanced analytics
- PostgreSQL database
- Password reset
- Resume attachment support

## Author

Virat GB

B.Tech – Electronics and Communication Engineering

GitHub:

https://github.com/VIRAT-GB