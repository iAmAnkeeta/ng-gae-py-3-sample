import os

# Set environment flag
IS_PROD = False
IS_LOCAL_HOST = True

# TODO generate secured key
FLASK_APP_SECRET = "6IdyGec28VeEaQlm1Bz05P0fZe9Ta"

# Ping configuration
APP_BASE_URL = "http://localhost:8080"

if "GOOGLE_CLOUD_PROJECT" in os.environ:
    APP_BASE_URL = f"https://{os.environ['GOOGLE_CLOUD_PROJECT']}.appspot.com"
    IS_PROD = os.environ['GOOGLE_CLOUD_PROJECT'] == os.environ['PROD_APP_ID']
    IS_LOCAL_HOST = False