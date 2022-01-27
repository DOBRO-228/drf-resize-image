install:
	poetry install
lint:
	poetry run flake8 backend
test:
	poetry run python3 manage.py test
sort:
	poetry run isort .
start:
	poetry run python3 manage.py runserver
start_gunicorn:
	poetry run gunicorn task_manager.wsgi
shell:
	poetry run python3 manage.py shell
make_migrations:
	poetry run python3 manage.py makemigrations
migrate:
	poetry run python3 manage.py migrate
export_req:
	poetry export -f requirements.txt --output requirements.txt
make_fixture:
	poetry run python3 manage.py dumpdata labels.Label --pk 1 --indent 4 > fixtures/labels.json