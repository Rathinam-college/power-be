# PowerTracker

A real-time energy monitoring and analysis platform.

## Project Overview
PowerTracker is designed to help users track, visualize, and analyze energy consumption data. It provides a robust backend for data management and a dynamic, modern frontend for visualization.

## Technology Stack

### Backend
- **Framework**: Django 6.0 + Django REST Framework (DRF)
- **Database**: PostgreSQL
- **Middleware**: CORS Headers for cross-origin resource sharing
- **Environment**: Managed via Python `venv` (`powertracker`)

### Frontend
- **Framework**: React 19 (Vite)
- **Styling**: Tailwind CSS v4
- **Charts**: Recharts
- **Icons**: Lucide React
- **HTTP Client**: Axios

---

## Project Structure
```text
PowerTracker/
├── core/               # Django project settings and URLs
├── frontend/           # React application (Vite)
│   ├── src/            # Source code (Components, Assets, Styles)
│   ├── index.html      # Frontend entry point
│   └── package.json    # Frontend dependencies and scripts
├── powertracker/       # Python virtual environment
├── manage.py           # Django management script
└── README.md           # Project documentation
```

---

## Setup and Installation

### Prerequisites
- Python 3.x
- Node.js & npm
- PostgreSQL

### Backend Setup
1. **Activate Virtual Environment**:
   ```powershell
   .\powertracker\Scripts\Activate.ps1
   ```
2. **Install Dependencies**:
   ```bash
   pip install django djangorestframework django-cors-headers psycopg2-binary
   ```
3. **Database Configuration**:
   Update `DATABASES` in `core/settings.py` with your PostgreSQL credentials.
4. **Run Server**:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup
1. **Navigate to Frontend**:
   ```bash
   cd frontend
   ```
2. **Install Dependencies**:
   ```bash
   npm install
   ```
3. **Run Development Server**:
   ```bash
   npm run dev
   ```

---

## Development Roadmap
1. [x] Project Initialization (Django & React)
2. [/] Core Documentation
3. [ ] Database Schema Design
4. [ ] API Endpoint Implementation
5. [ ] Frontend Dashboard UI
6. [ ] Integration and Testing
