# GovScheme Navigation

A Django web application designed to help citizens discover, search, and navigate various government schemes and benefits based on eligibility criteria.

## Features

- **Scheme Discovery & Search**: Browse and filter through government welfare schemes.
- **Eligibility Checking**: Find schemes tailored to demographic and socioeconomic parameters.
- **Scheme Seeding**: Built-in management command to seed scheme data (`seed_schemes`).

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Hemavarshiniramalingam/GovScheme_navigation.git
   cd GovScheme_navigation
   ```

2. **Create and activate a virtual environment:**
   - **Windows:**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations:**
   ```bash
   cd GovScheme_Navigation
   python manage.py migrate
   ```

5. **(Optional) Seed scheme data:**
   ```bash
   python manage.py seed_schemes
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. Access the application at `http://127.0.0.1:8000/`.
