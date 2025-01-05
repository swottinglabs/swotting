#!/bin/bash

# Start Django server
python manage.py runserver & 

# Start React development server
cd frontend && npm start &

# Wait for both processes
wait
