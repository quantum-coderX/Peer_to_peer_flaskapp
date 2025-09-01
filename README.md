# Peer-to-Peer Learning Platform

A Flask-based web application that connects users who want to learn skills with those who can teach them. This platform facilitates peer-to-peer knowledge exchange and community learning.

## About the Project

This project was developed as part of a DBMS lab assignment. It demonstrates the implementation of a full-stack web application with user authentication, database management, and interactive features using Flask and SQLAlchemy.

## Features

- **User Management**

  - Registration and authentication
  - Secure password handling with hashing
  - User profiles with skill information

- **Skill Exchange**

  - Add skills you can teach or want to learn
  - Set skill proficiency levels (1-5)
  - Find teachers or learners based on skills

- **Connection Management**

  - Request connections with potential teachers or learners
  - Accept or decline connection requests
  - View all active connections

- **Resource Sharing**
  - Share learning resources with your connections
  - Organize resources by skill/topic
  - Access shared resources from your dashboard

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

### Setting Up Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Initialize the Database

The SQLite database will be automatically created when you run the application for the first time. If you need to reset the database, you can delete the `peer_to_peer.db` file and restart the application.

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

## Database Structure

The application uses SQLAlchemy ORM with the following models:

- **User**: Stores user account information (username, email, password hash)
- **Skill**: Catalog of all available skills (name, description)
- **UserSkill**: Maps users to skills they can teach or want to learn (user_id, skill_id, is_teacher, skill_level)
- **Connection**: Tracks learning relationships between users (teacher_id, learner_id, skill_id, status)
- **Resource**: Stores learning materials shared by users (title, description, url, user_id, skill_id)

## Development Log

### Phase 1: Foundation (August 29-30, 2025)

- Set up the initial Flask application structure
- Created basic templates with template inheritance
- Implemented user authentication system with Flask-Login
- Configured SQLite database with SQLAlchemy
- Set up version control with Git

### Phase 2: Core Functionality (August 31, 2025)

- Designed and implemented database models for skills, connections, and resources
- Created dashboard interface for logged-in users
- Implemented skill management (adding skills to teach or learn)
- Built connection request system for matching teachers and learners
- Added resource sharing functionality

### Phase 3: UI Enhancements (September 1, 2025)

- Improved template styling with Bootstrap
- Fixed CSS issues with dynamic content
- Standardized form styling across the application
- Enhanced dashboard with better visual indicators for skill levels
- Optimized mobile responsiveness

## Technology Stack

- **Backend**: Flask 3.x (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Form Handling**: Flask-WTF
- **Data Serialization**: Flask-Marshmallow
- **Frontend**: Bootstrap 5.3 with custom CSS
- **Templates**: Jinja2
- **Database Migrations**: Flask-Migrate

## Usage Guide

### 1. Registration and Login

- Create a new account via the Register page
- Log in with your email and password

### 2. Managing Your Skills

- From the dashboard, add skills you can teach
- Add skills you want to learn
- For each skill, set your proficiency level (1-5)

### 3. Finding Connections

- Use the "Find Connections" page to discover potential teachers or learners
- Filter users by skill
- Send connection requests to users that match your learning needs

### 4. Sharing Resources

- Share helpful learning resources with your connections
- Include links to articles, videos, or other learning materials
- Organize resources by skill for easy discovery

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask documentation and community
- SQLAlchemy documentation
- Bootstrap team for the frontend framework
