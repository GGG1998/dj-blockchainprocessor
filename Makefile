old_test:
	echo "Running backend tests"
	echo "Depracted !!! due to problem with run pytest_celery"
	MODE=DEV poetry run ./manage.py test --settings=blockchainprocessor.settings

test:
	echo "Running backend tests"
	MODE=DEV pytest
	
celery:
	echo "Running celery"
	CELERY_RDBSIG=1 poetry run celery -A blockchainprocessor worker -l debug -P gevent -c 1
	
celery-beat:
	echo "Running celery beat"
	poetry run celery -A blockchainprocessor beat -l info