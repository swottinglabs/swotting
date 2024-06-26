# Stage 1: Build stage
FROM python:3.11-bullseye as build

# Install pip and wheel
RUN pip install -U pip wheel

# Set the working directory
WORKDIR /app

# Copy the project files to the container
COPY . .

# Install the dependencies and create wheels
RUN pip wheel --wheel-dir=/wheels /app

# Stage 2: Production stage
FROM python:3.11-slim-bullseye

# Set environment variables
ENV STATIC_ROOT=/app/static/

# Set the working directory
WORKDIR /app

# Copy the wheels from the build stage
COPY --from=build /wheels /wheels
COPY --from=build /app /app

# Install the dependencies from wheels
RUN pip install --no-index --find-links=/wheels swotting

# Collect static files
RUN python manage.py collectstatic --no-input

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "-b", "0.0.0.0:8000", "--capture-output", "--timeout", "120", "swotting.wsgi"]


# FROM python:3.11-bullseye as build

# RUN pip install -U pip wheel

# COPY . /app

# RUN pip wheel --wheel-dir=/wheels /app


# FROM python:3.11-slim-bullseye

# ENV STATIC_ROOT /app/static/
# COPY --from=build /wheels /wheels
# RUN pip install swotting --no-index --find-links /wheels
# RUN manage.py collectstatic --no-input
# WORKDIR /app

# EXPOSE 8000

# CMD ["gunicorn", "-b", "0.0.0.0:8000", "--capture-output", "--timeout", "120", "swotting.wsgi"]