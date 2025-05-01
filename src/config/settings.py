import os

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "MY_SECRET_KEY",  # TODO: generate a secret key and use here
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
