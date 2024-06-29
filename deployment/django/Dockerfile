# Use an official Python runtime as a parent image
FROM python:3.11-bullseye as builder

# Upgrade pip and install wheels
RUN pip install --upgrade pip wheel setuptools

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    cargo

# Set the working directory in the builder stage
WORKDIR /app

# Copy only the requirements file, to cache the pip install step
COPY requirements.txt /app/
RUN pip wheel --no-cache-dir --wheel-dir=/root/wheels -r requirements.txt

# Ensure gunicorn is installed
RUN pip install gunicorn

# Now, copy the wheels and other required files to the second stage
FROM python:3.11-slim-bullseye

WORKDIR /app

# Set static root
ENV STATIC_ROOT=/app/static/

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl1.1 \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built wheels from the builder stage
COPY --from=builder /root/wheels /root/wheels
COPY --from=builder /app/requirements.txt /app/

# Install the packages from wheels
RUN pip install --no-cache-dir --find-links=/root/wheels -r requirements.txt

# Copy the Django project (ensure all necessary files are included in your .dockerignore to avoid copying unnecessary files)
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --no-input

# Expose the port the app runs on
EXPOSE 8000

# Start Gunicorn with the specified settings
CMD ["gunicorn", "-b", "0.0.0.0:8000", "--capture-output", "--timeout", "120", "swotting.wsgi"]


# # Use an official Python runtime as a parent image
# FROM python:3.11-bullseye as builder

# # Upgrade pip and install wheels
# RUN pip install --upgrade pip wheel

# # Install build dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libssl-dev \
#     libffi-dev \
#     python3-dev \
#     cargo

# # Set the working directory in the builder stage
# WORKDIR /app

# # Copy only the requirements file, to cache the pip install step
# COPY requirements.txt /app/
# RUN pip wheel --no-cache-dir --no-deps --wheel-dir=/root/wheels -r requirements.txt

# # Now, copy the wheels and other required files to the second stage
# FROM python:3.11-slim-bullseye

# WORKDIR /app

# # Set static root
# ENV STATIC_ROOT=/app/static/

# # Install runtime dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libssl1.1 \
#     && rm -rf /var/lib/apt/lists/*

# # Copy pre-built wheels from the builder stage
# COPY --from=builder /root/wheels /root/wheels
# COPY --from=builder /app/requirements.txt /app/

# # Install the packages from wheels
# RUN pip install --no-cache-dir --no-index --find-links=/root/wheels -r requirements.txt

# # Copy the Django project (ensure all necessary files are included in your .dockerignore to avoid copying unnecessary files)
# COPY . /app/

# # Collect static files
# RUN python manage.py collectstatic --no-input

# # Expose the port the app runs on
# EXPOSE 8000

# # Start Gunicorn with the specified settings
# CMD ["gunicorn", "-b", "0.0.0.0:8000", "--capture-output", "--timeout", "120", "swotting.wsgi"]

# # Use an official Python runtime as a parent image
# FROM python:3.11-bullseye as builder

# # Upgrade pip and install wheels
# RUN pip install --upgrade pip wheel

# # Set the working directory in the builder stage
# WORKDIR /app

# # Copy only the requirements file, to cache the pip install step
# COPY requirements.txt /app/
# RUN pip wheel --no-binary :all: --wheel-dir=/root/wheels -r requirements.txt

# # Now, copy the wheels and other required files to the second stage
# FROM python:3.11-slim-bullseye

# WORKDIR /app

# # Set static root
# ENV STATIC_ROOT=/app/static/

# # Copy pre-built wheels from the builder stage
# COPY --from=builder /root/wheels /root/wheels
# COPY --from=builder /app/requirements.txt /app/

# # Install the packages from wheels
# RUN pip install --no-index --find-links=/root/wheels -r requirements.txt

# # Copy the Django project (ensure all necessary files are included in your .dockerignore to avoid copying unnecessary files)
# COPY . /app/

# # Collect static files
# RUN python manage.py collectstatic --no-input

# # Expose the port the app runs on
# EXPOSE 8000

# # Start Gunicorn with the specified settings
# CMD ["gunicorn", "-b", "0.0.0.0:8000", "--capture-output", "--timeout", "120", "swotting.wsgi"]


# FROM python:3.11-bullseye as build

# RUN pip install -U pip wheel

# WORKDIR /app
# COPY requirements.txt /app/requirements.txt
# RUN pip install -r requirements.txt

# COPY . /app
# RUN pip wheel --wheel-dir=/wheels /app

# FROM python:3.11-slim-bullseye

# ENV STATIC_ROOT /app/static/
# WORKDIR /app

# COPY --from=build /wheels /wheels
# COPY --from=build /app /app

# RUN pip install swotting --no-index --find-links /wheels
# RUN python manage.py collectstatic --no-input

# EXPOSE 8000

# CMD ["gunicorn", "-b", "0.0.0.0:8000", "--capture-output", "--timeout", "120", "swotting.wsgi"]


# FROM python:3.11-bullseye as build

# RUN pip install -U pip wheel

# WORKDIR /app
# COPY requirements.txt /app/requirements.txt
# RUN pip install -r requirements.txt

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