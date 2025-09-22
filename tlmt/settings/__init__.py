import os

env = os.getenv("ENV", "local")  # "production" ou "local"

if env == "production":
    from .prod import *
else:
    from .dev import *