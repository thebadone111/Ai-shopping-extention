import os

os.environ["SECRET_KEY"] = "secret"

print(os.environ.get("SECRET_KEY"))