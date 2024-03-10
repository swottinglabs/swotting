FROM python:3.11-bullseye as build

RUN pip install -U pip wheel

COPY . /app

RUN pip wheel --wheel-dir=/wheels /app


FROM python:3.11-slim-bullseye

ENV STATIC_ROOT /app/static/
COPY --from=build /wheels /wheels
RUN pip install swotting --no-index --find-links /wheels
RUN manage.py collectstatic --no-input
WORKDIR /app

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "--capture-output", "--timeout", "120", "beeline.wsgi"]