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

# Init DB Data
python manage.py init_db_data


# Get the database running
1. Install postgres
2. create postgres user and password user (should be there by default): postgres password: postgres
// create database from scraped csv file
3. python manage.py create_base_data path-to-file
4. python manage.py create_resources_from_csv path-to-file


# Random Notes
- when installing it on a new droplet. Some things to consisder: 
    - To get cert for new domain run: sudo certbot --nginx -d swotting.org -d www.swotting.org
    - you need to create a new superuser on the new droplet by running: docker compose exec web python manage.py createsuperuser
    - then run python manage.py init_db_data
- The python manage.py migrate command in the .github/workflows/main.yml file drasticaly slowed down the deployment.
    - 
