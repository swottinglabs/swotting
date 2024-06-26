FROM python:3.11-bullseye as build

RUN pip install -U pip wheel

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app
RUN pip wheel --wheel-dir=/wheels /app

FROM python:3.11-slim-bullseye

ENV STATIC_ROOT /app/static/
WORKDIR /app

COPY --from=build /wheels /wheels
COPY --from=build /app /app

RUN pip install swotting --no-index --find-links /wheels
RUN python manage.py collectstatic --no-input

EXPOSE 8000

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