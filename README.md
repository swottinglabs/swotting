# swotting
🚀 Swotting: Your Dual-Force in Learning! 🌐 A rich library and robust API rolled into one, Swotting offers unparalleled access to diverse educational resources. Ideal for EdTech platforms, businesses, and learners in SA and beyond. Elevate education with us! 📚✨ #LearningRevolution

# Project Setup Instructions

This guide will walk you through the steps to clone and run the Django/Scrapy project on your local machine.

## Prerequisites

Ensure you have the following installed on your system:
- Python 3
- pip (Python package installer)
- Git (version control system)

## Step 1: Clone the Repository


First, clone the project repository using Git:

git clone <your-repository-url>
cd swotting

## Step 2: Create a Virtual Environment

Navigate to the project's root directory and create a Python virtual environment named `venv`:

python3 -m venv venv

## Step 3: Activate the Virtual Environment
(Mac/Linux): source venv/bin/activate

## Step 4: Install Project Dependencies
pip install -r requirements.txt

## Step 5: Initialize the Database
python manage.py migrate

## Step 6: Create a Superuser Account
python manage.py createsuperuser

## Step 7: Run the Development Server
python manage.py runserver

## Step 8: Running Scrapy Spiders
To run a Scrapy spider, use the Django management command:

python manage.py scrape <spider_name>


