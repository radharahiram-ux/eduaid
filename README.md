EduAid
Show Image
Show Image
Overview
EduAid is an intelligent educational support platform designed to identify at-risk students and connect them with resources to succeed. By leveraging machine learning and data analytics, EduAid empowers teachers, schools, and NGOs to collaborate in preventing student dropouts and improving academic outcomes.
Key Features
🎯 Predictive Dropout Analytics

AI-Powered Risk Assessment: Machine learning algorithms analyze student data to predict dropout risk with high accuracy
Early Warning System: Identifies struggling students before they fall too far behind
Data-Driven Insights: Comprehensive analysis of attendance, grades, behavior, and socioeconomic factors

👨‍🏫 Comprehensive Teacher Dashboard

Real-Time Monitoring: Track student performance and engagement metrics at a glance
Individual Student Profiles: Detailed view of each student's academic journey and risk factors
Intervention Tracking: Monitor the effectiveness of support measures and interventions
Customizable Alerts: Receive notifications when students show warning signs

🤝 NGO Collaboration Platform

Resource Matching: Connect at-risk students with appropriate NGO support services
Financial Aid Coordination: Facilitate scholarship and financial assistance programs
Mentorship Programs: Link students with mentors for guidance and support
Transparent Communication: Streamlined coordination between schools and partner organizations

📊 GPA & Performance Tracking

Comprehensive Analytics: Monitor GPA trends, subject-wise performance, and improvement areas
Visual Dashboards: Interactive charts and graphs for easy interpretation
Progress Reports: Generate detailed reports for students, parents, and administrators
Comparative Analysis: Benchmark individual and class performance against standards

Tech Stack
Backend

Python - Core programming language
Flask - Lightweight web framework
SQLAlchemy - Database ORM for data management
Pandas - Data manipulation and analysis
Scikit-learn - Machine learning model implementation

Frontend

HTML5/CSS3 - Modern, responsive interface design
JavaScript - Interactive user experience
Bootstrap - Responsive UI components

Database

SQLite (Development) / PostgreSQL (Production) - Reliable data storage

Machine Learning

Classification Algorithms - Dropout prediction models
Feature Engineering - Data preprocessing and optimization
Model Evaluation - Cross-validation and performance metrics

Installation & Setup
Prerequisites

Python 3.8 or higher
pip (Python package manager)
Git

Step 1: Clone the Repository
bashgit clone https://github.com/yourusername/eduaid.git
cd eduaid
Step 2: Create a Virtual Environment
bash# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
Step 3: Install Dependencies
bashpip install -r requirements.txt
Step 4: Set Up Environment Variables
Create a .env file in the root directory:
envFLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///eduaid.db
Step 5: Initialize the Database
bashflask db init
flask db migrate -m "Initial migration"
flask db upgrade
Step 6: Seed Sample Data (Optional)
bashpython seed_data.py
Step 7: Run the Application
bashflask run
The application will be available at http://localhost:5000
Usage
For Teachers

Login: Access your teacher dashboard with provided credentials
View Students: Browse the list of students with risk indicators
Analyze Data: Review individual student profiles and performance metrics
Request Support: Submit requests for NGO assistance for at-risk students
Track Progress: Monitor the impact of interventions over time

For Administrators

Manage Users: Add/remove teachers, students, and NGO partners
Configure Settings: Adjust risk thresholds and notification preferences
Generate Reports: Create comprehensive reports for stakeholders
Monitor System: Oversee platform usage and performance

For NGOs

Review Requests: Access student support requests from partner schools
Provide Resources: Offer financial aid, mentorship, or other services
Track Impact: Monitor outcomes of your support programs
Communicate: Maintain direct contact with schools and coordinators

Project Structure
eduaid/
├── app.py                  # Main application entry point
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── models/                 # Database models
│   ├── student.py
│   ├── teacher.py
│   └── ngo.py
├── routes/                 # Application routes
│   ├── auth.py
│   ├── dashboard.py
│   └── api.py
├── ml_models/             # Machine learning components
│   ├── predictor.py
│   └── data_processor.py
├── static/                # Static assets
│   ├── css/
│   ├── js/
│   └── images/
├── templates/             # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   └── student_profile.html
└── tests/                 # Unit and integration tests
    ├── test_models.py
    └── test_routes.py
Contributing
We welcome contributions from the community! Here's how you can help:
Reporting Issues

Use the GitHub Issues tab to report bugs
Provide detailed descriptions and steps to reproduce
Include screenshots if applicable

Submitting Pull Requests

Fork the repository
Create a new branch (git checkout -b feature/your-feature-name)
Make your changes and commit (git commit -m 'Add some feature')
Push to your branch (git push origin feature/your-feature-name)
Open a Pull Request

Code Standards

Follow PEP 8 style guidelines for Python code
Write clear, descriptive commit messages
Include unit tests for new features
Update documentation as needed

Testing
Run the test suite:
bash# Run all tests
pytest

# Run with coverage report
pytest --cov=app tests/

# Run specific test file
pytest tests/test_models.py
Roadmap

 Mobile application for iOS and Android
 Multi-language support
 Advanced analytics with deep learning models
 Integration with popular LMS platforms
 Parent portal for family engagement
 SMS/email notification system

License
This project is licensed under the MIT License - see the LICENSE file for details.
Acknowledgments

Thanks to all educators who provided insights during development
Special recognition to partner NGOs for their collaboration
Built with support from educational technology researchers

Contact
For questions, suggestions, or support:

Email: support@eduaid.org
Website: https://eduaid.org
GitHub Issues: https://github.com/yourusername/eduaid/issues


Made with ❤️ for educators and students everywhere
