install:
	poetry install
lint:
	poetry run flake8 images
test:
	poetry run python3 manage.py test images.tests.view_tests images.tests.validation_tests images.tests.mixin_methods_tests
sort:
	poetry run isort .
start:
	poetry run python3.10 manage.py runserver
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
flush_db:
	poetry run python3 manage.py flush 