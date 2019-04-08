import os
from services.config import IS_LOCAL_HOST


def activate_virtual_env():
    """
    Activate virtual environment for localhost
    """
    if IS_LOCAL_HOST:
        cwd = os.getcwd()
        if cwd.endswith("/server"):
            # If you change the directory to server
            activate_this = "{cwd}/env/bin/activate_this.py".format(cwd=cwd)
        else:
            # If you running from the root directory of the project/repository
            activate_this = "{cwd}/server/env/bin/activate_this.py".format(cwd=cwd)
        exec(open(activate_this).read(), {'__file__': activate_this})