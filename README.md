# GYMO - Gym Management System

A comprehensive full-stack gym management system built with Python, designed to streamline gym operations, manage member training sessions, and provide real-time training dashboards.

## 🏋️ Overview

GYMO is a modern gym management platform that enables:

- **Member Management**: Profile management, training preferences, and session tracking
- **Training Scheduling**: Automated weekly schedule generation based on member preferences
- **Live Training Dashboard**: Real-time exercise tracking and progress monitoring
- **Class Management**: Group fitness classes booking and management
- **Multi-role Access**: Different interfaces for members, trainers, and managers

## 🛠️ Technology Stack

### Frontend

- **Framework**: NiceGUI (Python-based UI framework)
- **Styling**: Tailwind CSS classes
- **Port**: 8080

### Backend

- **Framework**: FastAPI (Python web framework)
- **API Documentation**: Automatic OpenAPI/Swagger documentation
- **Port**: 8000

### Database

- **Database**: MySQL
- **ORM**: Native MySQL connector with connection pooling
- **Architecture**: CRUD operations with separate database layer

### Authentication

- **Provider**: Auth0
- **Storage**: JWT tokens in localStorage
- **Session Management**: Starlette SessionMiddleware

## 📁 Project Structure

```
SemesterProject/
├── backend/
│   ├── api.py                      # FastAPI application entry point
│   ├── auth.py                     # Authentication handlers
│   ├── database/
│   │   ├── base.py                 # Database connection and pooling
│   │   ├── db_utils.py             # Database utilities
│   │   ├── crud/                   # CRUD operations
│   │   │   ├── class_mgmt.py       # Class management operations
│   │   │   ├── facilities.py       # Gym facilities and hours
│   │   │   ├── membership.py       # Membership management
│   │   │   ├── scheduling.py       # Training scheduling logic
│   │   │   ├── training_blueprints.py # Training plans and exercises
│   │   │   ├── training_execution.py  # Live sessions and workout logging
│   │   │   └── user.py             # User management
│   │   └── sql_queries/            # SQL query files
│   ├── routes/                     # API route handlers
│   │   ├── classes.py              # Class management routes
│   │   ├── custom_requests.py      # Custom training requests
│   │   ├── facilities.py           # Gym facilities routes
│   │   ├── finance.py              # Financial transactions
│   │   ├── notifications.py        # Notification system
│   │   ├── scheduling.py           # Training scheduling routes
│   │   ├── training_blueprints.py  # Training plans routes
│   │   ├── training_execution.py   # Live training routes
│   │   └── users.py                # User management routes
│   └── utils/
│       ├── oauth.py                # OAuth utilities
│       └── session.py              # Session management
├── frontend/
│   ├── config.py                   # Configuration settings
│   ├── ui.py                       # Main UI application
│   ├── components/
│   │   └── navbar.py               # Navigation component
│   ├── pages/                      # Application pages
│   │   ├── about.py                # About page with gym info
│   │   ├── classes.py              # Class management page
│   │   ├── full_details.py         # User profile completion
│   │   ├── home_page.py            # Landing page
│   │   ├── live_dashboard.py       # Real-time training dashboard
│   │   ├── member_preferences.py   # Member preference settings
│   │   ├── my_bookings.py          # User's class bookings
│   │   ├── my_training_plans.py    # User's training plans
│   │   ├── profile.py              # User profile management
│   │   ├── training.py             # Training plans overview
│   │   ├── training_preferences.py # Weekly training preferences
│   │   └── weekly_schedule.py      # Weekly training schedule
│   └── static/
│       └── callback.html           # Auth0 callback handler
├── main2.py                        # Application launcher
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- MySQL database
- Auth0 account for authentication

### 1. Clone the Repository

```bash
git clone <repository-url>
cd SemesterProject
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

1. Create a MySQL database
2. Execute the SQL scripts in `backend/database/sql_queries/` to create tables
3. Configure database connection in `.env` file:

```env
MYSQL_HOST=localhost
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=gym_management
MYSQL_PORT=3306
```

### 4. Auth0 Configuration

Create a `.env` file with your Auth0 credentials:

```env
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
AUTH0_DOMAIN=your_domain
AUTH0_AUDIENCE=your_audience
```

### 5. Environment Variables

```env
API_HOST=127.0.0.1
API_PORT=8000
UI_PORT=8080
APP_SECRET_KEY=your_secret_key
```

## 🏃 Running the Application

### Start the Backend (FastAPI)

```bash
uvicorn backend.api:api --host 127.0.0.1 --port 8000 --reload
```

### Start the Frontend (NiceGUI)

```bash
python -m frontend.ui
```

### Access the Application

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 👥 User Roles & Features

### 🏃 Members

- **Profile Management**: Complete profile with fitness goals and health conditions
- **Training Preferences**: Set weekly training preferences (available on Thursdays)
- **Weekly Schedule**: View assigned training sessions
- **Live Dashboard**: Real-time training session with exercise details, sets, reps, and weights
- **Class Bookings**: Book and manage group fitness classes
- **Progress Tracking**: View workout history and progress

### 🏋️ Trainers

- **Schedule Management**: View weekly training schedule and assigned members
- **Live Sessions**: Start and manage live training sessions
- **Member Progress**: Monitor member attendance and workout completion
- **Training Plans**: Create and manage training blueprints
- **Exercise Library**: Access comprehensive exercise database

### 👨‍💼 Managers

- **Dashboard Overview**: Real-time view of all gym activities
- **Schedule Generation**: Generate weekly schedules based on member preferences
- **Resource Management**: Manage halls, equipment, and trainer assignments
- **Analytics**: View gym usage statistics and revenue reports
- **User Management**: Manage member and trainer accounts

## 🔧 Key Features

### 📅 Smart Scheduling System

- **Preference Collection**: Members set preferences every Thursday
- **Automated Scheduling**: System generates optimal weekly schedules considering:
  - Member preferences and availability
  - Trainer availability and specializations
  - Hall capacity and equipment requirements
  - Optimal time slot distribution

### 📱 Live Training Dashboard

- **Real-time Tracking**: Live exercise tracking during training sessions
- **Exercise Details**: Complete exercise information with sets, reps, weights, and rest periods
- **Progress Monitoring**: Track completed vs. prescribed workouts
- **Adaptive Planning**: Adjust training plans based on performance

### 🎯 Training Management

- **Custom Training Plans**: Create personalized training blueprints
- **Exercise Library**: Comprehensive database of exercises with detailed instructions
- **Progress Tracking**: Log and monitor workout completion
- **Plan Adaptation**: Modify plans based on member progress

### 📊 Analytics & Reporting

- **Member Analytics**: Track attendance, progress, and engagement
- **Trainer Performance**: Monitor trainer effectiveness and member satisfaction
- **Facility Usage**: Optimize hall and equipment utilization
- **Financial Reports**: Revenue tracking and membership analytics

## 🗃️ Database Schema

### Core Tables

- **users**: Base user information
- **members**: Member-specific data (fitness goals, health conditions)
- **trainers**: Trainer profiles and specializations
- **managers**: Manager roles and departments

### Training System

- **training_plans**: Training blueprint templates
- **training_plan_days**: Daily training structure
- **training_day_exercises**: Exercise prescriptions
- **exercises**: Exercise library with instructions

### Scheduling System

- **training_preferences**: Member weekly preferences
- **weekly_schedule**: Generated training schedule
- **schedule_members**: Member-schedule assignments
- **live_sessions**: Active training sessions

### Class Management

- **classes**: Group fitness classes
- **class_types**: Class categories
- **class_bookings**: Member class registrations
- **halls**: Training facility spaces

### Progress Tracking

- **logged_workouts**: Completed workout sessions
- **logged_workout_exercises**: Exercise completion details
- **live_session_attendance**: Session attendance tracking

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-based Access**: Different permissions for members, trainers, and managers
- **Session Management**: Secure session handling with automatic expiration
- **Data Validation**: Input validation and sanitization
- **CORS Protection**: Cross-origin request security

## 📡 API Documentation

The API is fully documented using OpenAPI/Swagger. Access the interactive documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main API Endpoints

#### Authentication

- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/callback` - Auth0 callback

#### Users

- `GET /users/{user_id}` - Get user details
- `GET /users/trainers` - Get all trainers
- `PUT /users/{user_id}` - Update user profile

#### Training Plans

- `GET /training-plans` - Get all training plans
- `POST /training-plans` - Create training plan
- `GET /training-plans/{plan_id}` - Get specific plan

#### Scheduling

- `POST /training-plans/preferences` - Set training preferences
- `GET /training-plans/preferences/check` - Check preference setting availability
- `GET /weekly-schedules-for-week/{date}` - Get weekly schedule

#### Live Training

- `POST /training-execution/live-sessions/start` - Start live session
- `GET /training/live/sessions/current` - Get current active session
- `POST /training-execution/logged-workouts` - Log completed workout

## 🎨 UI/UX Features

- **Responsive Design**: Works on desktop and mobile devices
- **Dark Theme**: Modern dark theme with blue accents
- **Real-time Updates**: Live data updates without page refresh
- **Interactive Components**: Dynamic forms and data visualization
- **Conditional Navigation**: Context-aware navigation based on user role and status

## 🔄 Workflow

### Weekly Training Cycle

1. **Thursday**: Members set training preferences for the following week
2. **Thursday Night**: System generates optimal weekly schedule
3. **Sunday-Thursday**: Training sessions occur according to schedule
4. **During Sessions**: Live tracking and progress monitoring
5. **Post-Session**: Automatic workout logging and progress updates

### Class Management

1. **Manager**: Creates and schedules group fitness classes
2. **Members**: Browse and book available classes
3. **Trainer**: Manages class attendance and progression
4. **System**: Tracks attendance and generates reports

## 🚧 Development Status

### ✅ Completed Features

- User authentication and authorization
- Profile management system
- Training plans and exercise library
- Class booking system
- Training preferences setting
- Weekly schedule generation
- Live training dashboard
- Basic reporting and analytics

### 🔄 In Progress

- Advanced analytics dashboard
- Mobile app development
- Payment integration
- Advanced scheduling algorithms

### 📋 Planned Features

- Nutrition tracking
- Social features and challenges
- Equipment maintenance tracking
- Advanced reporting tools
- Integration with fitness wearables

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support, please contact the development team or create an issue in the repository.

---

**GYMO - Transforming Gym Management, One Workout at a Time** 🏋️‍♂️
