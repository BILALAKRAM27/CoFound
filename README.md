# CoFound: Entrepreneur & Investor Platform

## Project Overview

**CoFound** is a professional networking platform built with Django, designed to connect entrepreneurs and investors. The platform enables users to collaborate, share ideas, build professional relationships, and accelerate startup growth. It is ideal for:
- **Entrepreneurs** seeking funding, mentorship, or partnerships.
- **Investors** looking for promising startups and networking opportunities.

**Purpose:**  
To provide a seamless, modern, and secure environment for networking, content sharing, real-time messaging, and collaboration in the startup ecosystem.

---

## Key Features

- **User Authentication**
  - Secure registration and login for both investors and entrepreneurs.
  - Role-based access and profile management.

- **Posting Content**
  - Create, edit, and delete posts with text and multiple media types (images, videos, documents).
  - Like, comment, and save posts.

- **Collaboration Requests**
  - Send and manage collaboration requests between users.

- **Messaging System**
  - Real-time or near real-time chat (Django Channels/WebSockets).
  - Multiple conversations, dynamic switching, and persistent chat history.

- **Follow/Unfollow Functionality**
  - Follow or unfollow users, view mutual connections, and receive suggestions.

- **Search & Filter**
  - Powerful search and filtering for startups and investors.
  - Search by name, email, industry, and more.

- **Theme Toggle Support**
  - Switch between light and dark modes for an optimal user experience.

---

## Project Directory Structure

```
/CoFound/                  # Django project settings and root config
  settings.py              # Project configuration and installed apps
  urls.py                  # URL routing for the project

/Entrepreneurs/            # Entrepreneur app
  models.py                # Entrepreneur models (User, Profile, Post, etc.)
  views.py                 # Entrepreneur views and business logic
  templates/Entrepreneurs/ # HTML templates for entrepreneur pages
  consumers.py             # WebSocket consumers for real-time features

/Investors/                # Investor app
  models.py                # Investor models (Profile, FundingRound, etc.)
  views.py                 # Investor views and business logic
  templates/Investors/     # HTML templates for investor pages
  consumers.py             # WebSocket consumers for real-time features

/static/                   # Static files (CSS, JS, images)
  css/                     # Custom stylesheets
  Investors/assests/       # Investor-specific images

templates/                 # Shared HTML templates
  base.html                # Main base template
  account/                 # Authentication templates
  messages/                # Messaging templates

manage.py                  # Django management script
requirements.txt           # Python dependencies
README.md                  # Project documentation
```
*Adjust the above if your actual structure differs.*

---

## Libraries & Technologies Used

- **Django**: High-level Python web framework for rapid development.
- **Django REST Framework** (if used): For building RESTful APIs.
- **Django Channels / Daphne**: WebSocket support for real-time messaging.
- **Bootstrap 5**: Responsive frontend styling and layout.
- **jQuery / Vanilla JS**: AJAX requests for follow/unfollow, search, and dynamic UI.
- **SQLite / PostgreSQL**: Database backends (SQLite for development, PostgreSQL for production).
- **Pillow**: Image processing for profile and post images.
- **django-allauth**: Social authentication (Google, LinkedIn, etc.).
- **FontAwesome / Bootstrap Icons**: Iconography.
- **Other dependencies**: See `requirements.txt` for a full list.

---

## Setup Instructions

### Prerequisites

- Python 3.8+
- Django 4.x
- Channels (for WebSocket support)
- SQLite (default) or PostgreSQL (recommended for production)
- Node.js & npm (for frontend build, if using custom JS/CSS)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd CoFound
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Unix/macOS:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (admin):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. **(Optional) Set environment variables:**
   - `SECRET_KEY`, `DEBUG`, `DATABASE_URL`, etc. (see `settings.py`)

---

## Running with Daphne (ASGI Server for WebSockets)

**What is Daphne?**

- Daphne is an ASGI server developed as part of the Django Channels project. It is used to serve Django applications that require asynchronous features, such as WebSockets for real-time communication.

**Why use Daphne in this project?**

- Django’s default `runserver` is sufficient for most development and testing, but it does **not** support WebSockets in production.
- Daphne is required to power real-time features like the messaging/chat system in CoFound, as it fully supports the ASGI protocol and WebSockets.

**How to run the server with Daphne:**

1. **Install Daphne (if not already installed):**
   ```bash
   pip install daphne
   ```

2. **Run the server using Daphne:**
   ```bash
   daphne CoFound.asgi:application
   ```
   - Replace `CoFound` with your Django project directory if different.
   - By default, Daphne runs on port 8000. To specify a different port:
     ```bash
     daphne -p 8080 CoFound.asgi:application
     ```

**Beginner Notes:**
- You can use Django’s `runserver` for local development and testing, but for any real-time features (like messaging), you should use Daphne in production or when testing WebSockets.
- Make sure your `asgi.py` is properly configured and Channels is in your `INSTALLED_APPS`.
- For full production deployment, consider using Daphne behind a process manager (like systemd) and a reverse proxy (like Nginx).

---

## Usage

- **Register/Login:**  
  Choose your role (Investor or Entrepreneur) and register. Login with your credentials.

- **Search Startups or Investors:**  
  Use the search bar in the navbar or dedicated search pages to find users by name, email, or industry.

- **Follow/Unfollow Users:**  
  Click the follow/unfollow button on user cards or profiles to manage your network.

- **Send Messages:**  
  Use the messaging page to start or continue conversations. Real-time updates and multiple conversations are supported.

- **Post Content:**  
  Create posts with text and media. Like, comment, and save posts for later.

- **Send Collaboration Requests:**  
  Use the collaboration features to request partnerships or mentorship.

---

## Future Improvements

- Group chat and channels
- Advanced search and filtering for posts and users
- Push notifications for new messages and activity
- Enhanced analytics and reporting for users
- Integration with third-party APIs (e.g., LinkedIn, Google Drive)
- Mobile app version

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request. For major changes, open an issue first to discuss what you would like to change.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Credits / References

- **Frameworks:** Django, Django Channels, Bootstrap 5
- **Libraries:** jQuery, Pillow, FontAwesome, Bootstrap Icons
- **References:**
  - [Django documentation](https://docs.djangoproject.com/)
  - [Django Channels](https://channels.readthedocs.io/)
  - [Bootstrap](https://getbootstrap.com/)
  - [Real-time chat tutorials and open-source Django projects](https://github.com/)
