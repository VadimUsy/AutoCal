# AutoCal - Automated Calendar Event Manager

A Flask-based web application for managing and syncing events to Google Calendar.

## 📁 Project Structure

```
AutoCal/
├── app/                          # Backend (Flask Application)
│   ├── __init__.py              # App factory and initialization
│   ├── config.py                # Configuration management
│   ├── api/                     # API endpoints and business logic
│   │   ├── __init__.py
│   │   ├── routes.py            # API route handlers
│   │   └── services.py          # Calendar service (Google API)
│   ├── auth/                    # Authentication module
│   │   ├── __init__.py
│   │   ├── oauth.py             # OAuth configuration
│   │   └── routes.py            # Auth routes (login/logout)
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   └── event.py             # Event dataclass
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       └── validators.py        # Input validation
│
├── frontend/                     # Frontend (All UI Assets)
│   ├── templates/               # HTML Templates
│   │   ├── base.html            # Base template
│   │   ├── events.html      # Main events page
│   │   └── components/          # Reusable components
│   │       ├── event_form.html  # Event creation form
│   │       └── event_list.html  # Event list sidebar
│   ├── css/
│   │   └── main.css             # Custom styles
│   └── js/
│       ├── main.js              # Main JavaScript entry
│       └── validation.js        # Form validation logic
│
├── flask_session/               # Session storage (gitignored)
├── venv/                        # Virtual environment (gitignored)
├── app.py                       # Application entry point
├── credentials.json             # OAuth credentials (gitignored)
├── requirements.txt             # Python dependencies
└── .gitignore                   # Git ignore rules
```

## ✨ Features

- **Google OAuth Authentication**: Secure login with Google
- **Event Management**: Add, view, and remove events
- **Calendar Sync**: Batch sync events to Google Calendar
- **Input Validation**: Client-side and server-side validation
- **Session Management**: File-based session storage
- **Responsive Design**: Mobile-friendly UI with Tailwind CSS

## 🏗️ Architecture

### Backend (Flask)
- **Application Factory Pattern**: Clean app initialization in [`app/__init__.py`](app/__init__.py)
- **Blueprint Architecture**: Modular routing
  - [`auth_bp`](app/auth/routes.py) - Authentication routes
  - [`api_bp`](app/api/routes.py) - API endpoints
- **Service Layer**: Business logic in [`CalendarService`](app/api/services.py)
- **Configuration Management**: Centralized in [`app/config.py`](app/config.py)
- **Type Safety**: Using dataclasses in [`app/models/event.py`](app/models/event.py)

### Frontend
- **Modular CSS**: Custom styles in [`frontend/css/main.css`](frontend/css/main.css)
- **ES6 Modules**: Modern JavaScript with imports
  - [`frontend/js/main.js`](frontend/js/main.js) - Application initialization
  - [`frontend/js/validation.js`](frontend/js/validation.js) - Form validation
- **Component-Based**: Reusable HTML components
  - [`frontend/templates/components/event_form.html`](frontend/templates/components/event_form.html)
  - [`frontend/templates/components/event_list.html`](frontend/templates/components/event_list.html)
- **Template Inheritance**: Base template with blocks

## 🚀 Setup

1. **Clone the Repository**:
   ```bash
   git clone <your-repo-url>
   cd AutoCal
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure OAuth**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google Calendar API
   - Create OAuth 2.0 credentials
   - Download credentials and save as `credentials.json` in the root directory

5. **Run the Application**:
   ```bash
   python app.py
   ```

6. **Access the App**:
   - Navigate to `http://localhost:5002`

## 🔧 Configuration

Edit [`app/config.py`](app/config.py) to customize:
- `LOCAL_TIMEZONE`: Your timezone (default: 'America/New_York')
- `DEFAULT_EVENT_DURATION_HOURS`: Event duration (default: 1 hour)
- Session settings and OAuth scopes

## 📝 API Routes

### Authentication (`/auth`)
- `GET /auth/login` - Initiate Google OAuth login
- `GET /auth/login/google/authorized` - OAuth callback
- `GET /auth/logout` - Clear session and logout

### API (root)
- `GET /` - Redirect to events or login
- `GET /events` - Display events page
- `POST /events/add` - Add new event to session
- `POST /events/remove` - Remove selected events
- `GET|POST /events/sync` - Sync events to Google Calendar

## 🎨 Frontend Components

### Templates
- **[base.html](frontend/templates/base.html)**: Base layout with CSS/JS imports
- **[events_new.html](frontend/templates/events_new.html)**: Main page extending base
- **[components/event_form.html](frontend/templates/components/event_form.html)**: Event creation form
- **[components/event_list.html](frontend/templates/components/event_list.html)**: Event list with checkboxes

### JavaScript Modules
- **[main.js](frontend/js/main.js)**: Application initialization
- **[validation.js](frontend/js/validation.js)**: Form validation logic (ranges, required fields)

### CSS
- **[main.css](frontend/css/main.css)**: Custom styles (theme colors, buttons, forms)

## 🔐 Security

- OAuth 2.0 authentication with Google
- Session-based authorization
- Input validation (client + server)
- CSRF protection via Flask-Session
- Credentials in `.gitignore`
- Secure token handling

## 📦 Dependencies

See [`requirements.txt`](requirements.txt) for full list:
- Flask 2.0.2
- Flask-Session 0.4.0
- Authlib 0.15.5
- google-auth 2.3.3
- google-api-python-client 2.26.1
- pytz 2021.3

## 🧪 Development

### Adding New Features

**Backend**:
1. Add routes to [`app/api/routes.py`](app/api/routes.py) or create new blueprint
2. Add business logic to [`app/api/services.py`](app/api/services.py)
3. Add models to [`app/models/`](app/models/)
4. Add validators to [`app/utils/validators.py`](app/utils/validators.py)

**Frontend**:
1. Add styles to [`frontend/css/main.css`](frontend/css/main.css)
2. Add JavaScript to [`frontend/js/`](frontend/js/)
3. Create components in [`frontend/templates/components/`](frontend/templates/components/)
4. Extend [`frontend/templates/base.html`](frontend/templates/base.html) for new pages

## 📄 License

[Your License Here]

## 🤝 Contributing

[Your Contributing Guidelines Here]
