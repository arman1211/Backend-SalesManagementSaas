from decouple import config

settings_module = config("DJANGO_SETTINGS_MODULE", default="config.settings.development")

if settings_module.endswith("production"):
    from .production import *  # noqa: F403
elif settings_module.endswith("development"):
    from .development import *  # noqa: F403
else:
    from .development import *  # noqa: F403
