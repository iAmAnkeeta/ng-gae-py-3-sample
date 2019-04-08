import multiprocessing

# Documentation
# http://docs.gunicorn.org/en/stable/settings.html#worker-processes
workers = multiprocessing.cpu_count() * 2 + 1