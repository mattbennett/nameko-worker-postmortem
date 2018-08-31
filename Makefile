test:
	coverage run --concurrency=eventlet --source nameko_worker_postmortem.py --branch -m pytest test.py
	# coverage report --show-missing --fail-under=100
