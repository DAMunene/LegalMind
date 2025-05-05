# Contract Analysis Platform

A Django-based web application that provides intelligent contract analysis and risk assessment using OpenAI's API.

## Features

- Secure contract upload and management
- Automated risk analysis using OpenAI
- Risk scoring and categorization
- Clause-level risk identification
- User authentication and authorization
- Modern responsive UI with Bootstrap
- File versioning and audit trail

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Node.js (for frontend dependencies)
- PostgreSQL (recommended) or SQLite
- OpenAI API key

## Installation

This project uses Docker for deployment. Follow these steps to set up the environment:

1. Clone the repository:
```bash
git clone https://github.com/DAMunene/LegalMind.git
cd LegalMind
```

2. Set up environment variables:
Create a `.env` file in the project root with the following content:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgres://postgres:postgres@db:5432/contract_db
OPENAI_API_KEY=your-openai-api-key
```

3. Build and run the Docker containers:
```bash
docker-compose build
docker-compose up -d
```

## Running the Application

1. After starting the containers with `docker-compose up -d`, the application will be available at:
   - Web interface: http://localhost:8080
   - API: http://localhost:8080/api/
   - Admin interface: http://localhost:8080/admin/

2. To create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

3. To run database migrations:
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

## Docker Commands

- Start containers: `docker-compose up -d`
- Stop containers: `docker-compose down`
- View logs: `docker-compose logs -f`
- Execute commands in web container: `docker-compose exec web <command>`
- Execute commands in database container: `docker-compose exec db <command>`

## Development

For local development without Docker:

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install django django-crispy-forms django-simple-jwt django-filter
django-environ djangorestframework psycopg2-binary
```

3. Run the development server:
```bash
python manage.py runserver
```

Note: The Docker setup is recommended for production and consistent development environments.

## Project Structure

```
contract-analysis-platform/
├── api/                 # Django app containing main application logic
│   ├── models.py       # Database models
│   ├── views.py        # API views
│   ├── template_views.py # Template-based views
│   ├── urls.py         # URL routing
│   ├── serializers.py  # Django REST framework serializers
│   └── services.py     # Business logic and OpenAI integration
├── core/               # Project configuration
│   ├── settings.py     # Django settings
│   ├── urls.py         # Root URL configuration
│   └── wsgi.py         # WSGI configuration
└── templates/          # HTML templates
```

## API Documentation

The application provides RESTful endpoints for contract management:

### Authentication

- POST `/api/auth/register/` - Register a new user
- POST `/api/auth/login/` - Login and get JWT tokens
- POST `/api/auth/logout/` - Logout and blacklist refresh token

### Contracts

- POST `/api/contracts/` - Upload and analyze a new contract
- GET `/api/contracts/` - List all user's contracts
- GET `/api/contracts/{id}/` - Get contract details
- PUT `/api/contracts/{id}/` - Update contract
- DELETE `/api/contracts/{id}/` - Delete contract

## Security

- JWT-based authentication
- User-based authorization
- File upload validation
- Rate limiting
- Secure password hashing
- CSRF protection
- XSS prevention

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact support@contract-analysis-platform.com
