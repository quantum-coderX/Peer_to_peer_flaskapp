# Peer-to-Peer Flask Application

As part of DBMS lab we have to submit a miniproject utilizing any DBMS.

## Installation and Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

### Clone the Repository

```bash
git clone https://github.com/quantum-coderX/Peer_to_peer_flaskapp.git
cd Peer_to_peer_flaskapp
```

### Set Up Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Initialize the Database

The database will be automatically created when you run the application for the first time.

## Running the Application

### Start the Development Server

```bash
python app.py
```

### Access the Application

Open your web browser and navigate to:

```
http://127.0.0.1:5000
```

## Features

- User registration and authentication
- Secure password handling with hashing
- Database storage of user information
- Responsive web interface

## Development Log

### Day 1 (August 29, 2025)

- Set up the initial Flask application structure
- Created basic templates with template inheritance
  - Layout template with navigation
  - Home page
  - Services page
  - Login page
  - Registration page
- Implemented user authentication system
  - Created registration form with validation
  - Set up login functionality
  - Added password hashing for security
- Configured SQLite database
  - Created User model
  - Implemented database storage for user registration
  - Added flash messages for user feedback
- Set up version control with Git
  - Added appropriate .gitignore file
  - Made initial commit of the project

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (Development), MySQL (Production)
- **Form Handling**: Flask-WTF
- **Data Serialization**: Flask-Marshmallow
- **ORM**: SQLAlchemy
- **Templates**: Jinja2
