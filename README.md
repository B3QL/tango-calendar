# Tango Calendar
A simple calendar app build using Django and DRF for recruitment process.

### Running application
Install poetry, see https://python-poetry.org/docs/#installation and execute following commands
```
poetry install
poetry shell
./manage.py migrate
./manage.py createsuperuser
./manage.py runserver
```
The API endpoints are located under:
* http://127.0.0.1:8000/api/events/
* http://127.0.0.1:8000/api/rooms/

Django REST Framework login page: http://127.0.0.1:8000/api/login/

Django admin: http://127.0.0.1:8000/admin/