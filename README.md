# 🏥 AccessHealth

> **🎓 Academic Project:** This application was developed as a school project for the **Interactive Web Development** (Semester 3) course in the Computer and Software Engineering program at the **University of Rwanda**.

> **🤖 Built with Vibe Coding:** The development process for this project embraced "vibe coding"—leveraging AI assistants to brainstorm logic, scaffold boilerplate code, and troubleshoot errors, allowing for a focus on high-level architecture and problem-solving.

AccessHealth is an interactive web application designed to [briefly describe the main goal, e.g., monitor patient health metrics, streamline doctor-patient communication, and provide intuitive health dashboards]. 

Built with Django, this platform provides both healthcare providers and patients with a secure, real-time overview of critical health readings and status indicators.

## ✨ Features

* **Patient Dashboard:** An interactive interface for patients to view their health metrics (e.g., device battery levels, sensor readings).
* **Real-time Status Indicators:** Visual cues (Green/Yellow/Red) for quick assessment of critical data points.
* **[Add Feature 3]:** [Description of feature, e.g., Secure User Authentication for Doctors and Patients].
* **[Add Feature 4]:** [Description of feature, e.g., Exportable Medical Reports].

## 🛠️ Tech Stack

* **Backend:** Python, Django
* **Frontend:** HTML5, CSS3, [JavaScript / Bootstrap / Tailwind - specify what you used]
* **Database:** [SQLite (default) / PostgreSQL / MySQL - specify what you used]

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Make sure you have Python installed on your system. You can download it from [python.org](https://www.python.org/).

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone [https://github.com/](https://github.com/)[your-username]/AccessHealth.git
   cd AccessHealth

2. **Create and activate a virtual environment**
   * **Windows:**
     `python -m venv venv`
     `venv\Scripts\activate`
   * **macOS/Linux:**
     `python3 -m venv venv`
     `source venv/bin/activate`

3. **Install dependencies**
   Ensure you have a `requirements.txt` file in your project.
   `pip install -r requirements.txt`

4. **Apply database migrations**
   `python manage.py migrate`

5. **Create a superuser (Admin)**
   `python manage.py createsuperuser`

6. **Run the development server**
   `python manage.py runserver`
   *Open your browser and navigate to `http://127.0.0.1:8000/` to view the app.*

## 📁 Project Structure

AccessHealth/
├── manage.py
├── AccessHealth/          # Main project settings
├── webapp/                # Main application directory
│   ├── templates/         # HTML templates
│   ├── static/            # CSS, JS, and image files
│   ├── models.py          # Database models
│   ├── views.py           # Application logic
│   └── urls.py            # Route definitions
└── requirements.txt       # Python dependencies
