# CoFound: Entrepreneur & Investor Platform

## Project Overview

CoFound is a Django-based web platform designed to connect entrepreneurs and investors, enabling them to collaborate, share ideas, and build the future together. The project aims to provide a seamless experience for networking, posting updates, managing profiles, and real-time messaging.

### Purpose and Goals
- Facilitate meaningful connections between entrepreneurs and investors.
- Provide a robust social platform with modern features: posts, comments, likes, messaging, and networking.
- Enable real-time communication and dynamic updates without page reloads.

### Main Functionalities
- **Dashboard:** Personalized overview for each user.
- **Posts:** Create, view, like, comment, and save posts with multiple media types.
- **Profiles:** Manage user profiles, including image uploads and editing.
- **Network:** Follow/unfollow users, view mutual friends, and discover new connections.
- **Messaging:** Real-time chat with multiple users, dynamic conversation switching, and persistent alignment.
- **Saved Posts:** Save and manage favorite posts for later reference.

---

## Features

- **User Registration & Login**
  - Separate flows for Investors and Entrepreneurs.
  - Secure authentication and role-based access.

- **Profile Management**
  - Upload profile images as BLOBs.
  - Edit profile details without requiring a new image.

- **Posts**
  - Create posts with text and multiple media (photos, videos, documents).
  - Like and comment on posts (with edit/delete for comments).
  - Save/unsave posts for quick access.

- **Network**
  - Follow/Following system with mutual friends logic.
  - Same-industry suggestions and “People You May Know” sidebar.

- **Messaging System**
  - Real-time or dynamic message sending (WebSocket/AJAX).
  - Multiple conversations with different users.
  - Messages aligned left/right based on sender.
  - Dynamic updates to conversations without page reload.
  - Scrollable message list with input fixed at the bottom and footer always below chat.

---

## Architecture and Models

### Key Models
- **User**: Abstract user with roles (Investor, Entrepreneur).
- **EntrepreneurProfile / InvestorProfile**: Extended user details, including profile image (BLOB).
- **Post**: User-generated content with text and media.
- **PostMedia**: Media files (image, video, document) attached to posts.
- **Comment**: Comments on posts, with author and edit/delete support.
- **Like**: Many-to-many relationship for post likes.
- **SavedPost**: Many-to-many for users saving posts.
- **Favorite (Connection)**: Follow/following relationships between users.
- **Message**: Direct messages between users, with sender, receiver, content, and media.

### Relationships
- Users can have one EntrepreneurProfile or InvestorProfile.
- Posts are authored by users; each post can have multiple media files.
- Comments and likes are linked to posts and users.
- Favorites represent network connections (follow/following).
- Messages are between two users, with a deterministic room/channel per pair.

---

## Frontend & Styling

- **Templates Used:**
  - `home.html`, `savedpost.html`, `profile.html`, `network.html`, `my_post.html`, messaging templates (`messages/index.html`, etc.)
- **Base Template:**
  - `base.html` provides the main structure, with `{% block content %}` for page-specific content.
  - Theme toggle functionality for light/dark mode.
- **Responsive Design:**
  - Uses Bootstrap 5 and custom CSS for responsive layouts.
  - Card-based layouts for posts, network suggestions, and media galleries.
- **Messaging UI:**
  - Scrollable message list, fixed input at bottom, and persistent footer below chat.
  - Dynamic alignment and avatar display for sender/receiver.

---

## Messaging Functionality (Detailed)

- **Sending & Receiving Messages:**
  - Uses Django Channels (WebSocket) for real-time updates.
  - Messages are sent to the backend and broadcast to both sender and receiver.
- **Conversation Switching:**
  - Users can switch between conversations without reloading the page.
  - WebSocket connections are cleaned up and re-established as needed.
- **Alignment Rules:**
  - Messages are aligned right if `sender_id == current_user_id`, left otherwise.
  - Alignment is preserved on reload and for historical messages.
- **Footer & Input Behavior:**
  - The message list is scrollable; the input area is always fixed at the bottom.
  - The site footer remains below the chat, never overlapping.
- **AJAX/WebSocket:**
  - WebSocket is used for real-time messaging; AJAX/fetch is used for loading message history and search.
- **Multiple Conversations:**
  - Users can have multiple active conversations, with dynamic updates and no page reloads.

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- Django 4.x
- Channels (for WebSocket support)
- SQLite (default) or PostgreSQL (recommended for production)
- Node.js & npm (for frontend build, if using custom JS/CSS)

### Setup Steps
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd CoFound
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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

## Usage Instructions

- **Register/Login:**
  - Choose Investor or Entrepreneur registration.
  - Login with your credentials.
- **Create/Edit Posts:**
  - Use the dashboard or posts page to create new posts with text and media.
  - Edit or delete your posts as needed.
- **Follow/Unfollow & Network:**
  - Use the network page to follow/unfollow users.
  - View mutual friends and same-industry suggestions in the sidebar.
- **Messaging:**
  - Open the messaging page to start or continue conversations.
  - Switch between users in the sidebar; messages update dynamically.
  - Messages are aligned based on sender, and the input area is always accessible.

---

## Screenshots / Visual Guide (Optional)

> _Add screenshots of the dashboard, posts, profile, network, and messaging pages here for a visual overview._

---

## Future Improvements

- Group chat and channels.
- Advanced search and filtering for posts and users.
- Push notifications for new messages and activity.
- Enhanced analytics and reporting for users.
- Integration with third-party APIs (e.g., LinkedIn, Google Drive).
- Mobile app version.

---

## Credits / References

- **Frameworks:** Django, Django Channels, Bootstrap 5
- **Libraries:** jQuery, FontAwesome, Bootstrap Icons
- **Tutorials/References:**
  - Django documentation: https://docs.djangoproject.com/
  - Django Channels: https://channels.readthedocs.io/
  - Bootstrap: https://getbootstrap.com/
  - Real-time chat tutorials and open-source Django projects
