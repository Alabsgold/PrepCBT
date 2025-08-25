Project Plan: CBT Practice Platform
1. Project Overview
This document outlines the plan for building a web-based Computer-Based Test (CBT) practice application. The platform will enable teachers to create and manage question banks and practice tests, while allowing students to take these tests in a simulated CBT environment, receive instant feedback, and track their performance.

The primary goal is to create a secure, robust, and user-friendly tool to help Nigerian students prepare for examinations like JAMB, WAEC, and university post-UTME tests.

2. Core Features (Minimum Viable Product - MVP)
To start, we will focus on the most essential features to make the app functional.

Teacher Portal:

Secure user registration and login.

A dashboard to view created quizzes.

Functionality to create, update, and delete quizzes (e.g., "COS 101 - Mock Exam 1").

A simple interface to add multiple-choice questions with four options, a correct answer, and a rationale to any quiz.

Student Portal:

Secure user registration and login.

A dashboard listing all available quizzes.

A clean, timed CBT interface for taking quizzes one question at a time.

An instant results page showing the final score upon submission.

A review page where students can see their answers, the correct answers, and the rationale for each question.

3. Technology Stack
As decided, we will use a simple, integrated approach to keep complexity to a minimum.

Backend: Python with the Django Framework.

Frontend: HTML, CSS, and JavaScript, rendered by Django's Templating Engine.

UI/UX Framework: Bootstrap 5 for a clean, responsive design without extensive custom CSS.

Database: SQLite for initial local development (easy to set up), with a plan to migrate to PostgreSQL for the live version.

4. Database Schema
This is the structure of our database. We'll start with four main tables.

User Table (Django's built-in)

id (Primary Key)

username

password

is_student (Boolean)

is_teacher (Boolean)

Quiz Table

id (Primary Key)

title (e.g., "JAMB Physics Practice")

subject (e.g., "Physics")

creator (Foreign Key to User table)

time_limit_minutes (Integer)

Question Table

id (Primary Key)

quiz (Foreign Key to Quiz table)

text (The question itself)

option_a

option_b

option_c

option_d

correct_answer (e.g., "A", "B", "C", or "D")

rationale (Text explaining the correct answer)

Result Table

id (Primary Key)

student (Foreign Key to User table)

quiz (Foreign Key to Quiz table)

score (Integer)

completed_on (Timestamp)

5. Next Steps
Set up the Local Development Environment:

Install Python.

Install Django.

Create a new Django project and app.

Implement User Authentication:

Configure Django's built-in user model to include roles for "student" and "teacher".

Create the registration and login pages.

Build the Teacher Portal:

Create the Django models for Quiz and Question.

Use Django's built-in Admin panel to provide an initial interface for teachers to add questions.

Build the Student Portal:

Create the views and templates for the student dashboard and the quiz-taking interface.
