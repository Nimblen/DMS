# Document Management System

This project is a web application for managing documents within an organization. It allows employees to upload documents, managers and assistants to review them, and provides a notification system and chat for communication.

## **Functionality**

- **Authentication and Authorization**: User registration, login, role-based access control (employee, manager, assistant).
- **Document Management**:
  - Employees can upload documents (only PDF files).
  - Managers and assistants can view and review documents.
  - Document statuses: under review, accepted, rejected.
- **Notification System**:
  - Notifications about new documents, status changes, and role change requests.
  - Notifications are sent in real-time using WebSocket.
- **Chat**: A shared chat for communication between users.
- **Role Change Requests**: Users can request a role change, and administrators can approve or reject requests.

## **Technologies**

- **Backend**:
  - Django 4.2
  - Django Channels
  - Redis (for channel layer and/or task broker)
- **Frontend**:
  - Bootstrap 4
  - django-crispy-forms
- **Database**:
  - PostgreSQL
- **Other**:
  - WebSocket for real-time communication

## **Installation and Setup**

### **Prerequisites**

- Python 3.9 or higher
- Redis (if using Redis as channel layer and/or task broker)
- Virtual environment (recommended)

### **Steps to Install**

1. **Clone the repository:**


### Clone the repository
   ```bash
    git clone https://github.com/nimblen/DMS.git
    cd DMS
   ```

### Create and activate a virtual environment
  ```bash
    python -m venv venv
  ```
  ```bash
    source venv/bin/activate  # For Linux/Mac
  ```
  ```bash
    venv\Scripts\activate  # For Windows
  ```

### Install dependencies
  ```bash
    pip install -r requirements.txt
  ```

### Apply database migrations
  ```bash
    python manage.py migrate
  ```
### Create a superuser
   ```bash
    python manage.py createsuperuser
   ```
### Run the development server
  ```bash
    daphne -p 8000 config.asgi:application
  ```

# Additional steps
# Ensure Redis is running on your machine or server
# Create database and user if they don't exist

### Collect static files if needed
  ```bash
    python manage.py collectstatic
  ```

## Usage
### Admin panel: Accessible at http://localhost:8000/admin/
### Main application: Accessible at http://localhost:8000/

### Project structure
### config/: Project settings, routes, and ASGI configuration
### users/: User management and authentication application
### documents/: Document management application
### notifications/: Notification system
### templates/: HTML templates
### static/: Static files (CSS, JS, images)
