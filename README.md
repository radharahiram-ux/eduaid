<div align="center">

# 🎓 EduAid

<img src="./eduaid_logo_1768302308390.png" alt="EduAid Logo" width="200"/>

### *AI-Powered Student Dropout Prevention Platform*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)](https://flask.palletsprojects.com/)

<img src="./eduaid_hero_banner_1768302326645.png" alt="EduAid Hero Banner" width="800"/>

</div>

---

## 📖 About

EduAid uses machine learning to identify at-risk students and connects them with NGO support. Teachers get early warnings, administrators track interventions, and NGOs provide targeted assistance.

## ✨ Features

- 🔮 **Predictive Analytics** - ML algorithms identify dropout risk before it's too late
- 👨‍🏫 **Teacher Dashboard** - Real-time student monitoring and performance tracking
- 🤝 **NGO Integration** - Connect students with financial aid and mentorship programs
- 📊 **GPA Tracking** - Comprehensive academic performance analytics

## 🛠️ Tech Stack

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit_Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

</div>

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/eduaid.git
cd eduaid

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Initialize database
flask db upgrade
python seed_data.py

# Run application
flask run
```

Visit `http://localhost:5000`

## 📁 Project Structure

```
eduaid/
├── app.py                 # Main application
├── models/                # Database models
├── routes/                # Application routes
├── ml_models/            # ML prediction engine
├── static/               # CSS, JS, images
├── templates/            # HTML templates
└── tests/                # Test suite
```

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📜 License

MIT License - see [LICENSE](LICENSE) file

## 📞 Contact

- **Email**: Kavyanshkrishan@gmail.com
- **Website**: [https://eduaid.org](https://eduaid.org)
- **Issues**: [GitHub Issues](https://github.com/radharahiram-ux/eduaid/issues)

---

<div align="center">

**Made with ❤️ for educators and students**

[⬆ Back to Top](#-eduaid)

</div>
