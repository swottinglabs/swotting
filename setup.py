from setuptools import setup, find_packages

setup(
    name='swotting',
    version='24.3.05',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'dj-database-url==2.1.0',
        'psycopg2-binary==2.9.5',
        # 'redis==5.0.4',
        'gunicorn==20.1.0',
        'requests==2.31.0',
        'Django==4.2.11',
        'django-cors-headers==3.14.0',
        'django-json-widget==1.1.1',
        'python-dotenv==1.0.0',
        # 'django-taggit==3.1.0',
        'django-lifecycle==1.0.0',
        # 'huey==2.5.0',
        'djangorestframework==3.14',
        'pydantic==2.5.2',
        'pydantic_core==2.14.5',
        'xmltodict==0.13.0',
        'beautifulsoup4==4.11.1',
        'Pillow==10.2.0',
        'coverage==7.0.3',
        'whitenoise==6.3.0',
        'pgvector==0.2.3',
    ],

    extras_require={
        'dev': [],
        'test': []
    },
    scripts=['manage.py'],
)
