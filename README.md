Blogposts API

The Blogposts API is a RESTful API built with Django and Django REST Framework. It allows users to create, retrieve, update, and delete blog posts, manage comments, like posts, and perform advanced features like JWT-based authentication and trending post metrics.

Features

User Authentication

Register new users.

Secure login with JWT tokens.


CRUD Operations

Manage blog posts with features like filtering, searching, and pagination.

Add, update, or delete comments on posts.


Post Interactions

Like and rate posts.

View trending posts based on likes, comments, and shares.


Notifications

Get notifications for key user activities.


Subscription System

Subscribe to posts or users for updates.




---

Installation

Prerequisites

Ensure you have the following installed:

Python 3.8+

Django 4.x

Django REST Framework

MySQL or any other supported database


Clone the Repository

git clone https://github.com/se-thato/blogposts_api.git
cd blogposts_api

Install Dependencies

1. Create a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


2. Install required Python packages:

pip install -r requirements.txt




---

Configuration

1. Update database settings in settings.py:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}


2. Apply migrations:

python manage.py makemigrations
python manage.py migrate


3. Create a superuser:

python manage.py createsuperuser


4. Run the development server:

python manage.py runserver




---

Endpoints

Authentication

Blog Posts

Comments

Likes and Ratings

Trending Posts


---

Technologies Used

Framework: Django, Django REST Framework

Database: MySQL

Authentication: JWT (via SimpleJWT)

Languages: Python



---

Development

Running Tests

Run the following command to execute unit tests:

python manage.py test

API Documentation

The API documentation is available via the DRF browsable API. Access it by visiting the server URL in your browser.


---

Contributing

1. Fork the repository.


2. Create a new branch for your feature/bugfix.


3. Commit your changes and push them to your branch.


4. Create a pull request.


