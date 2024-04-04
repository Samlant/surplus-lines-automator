from helper import LOG_FILE


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            # "style": "$",
        },
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.FileHandler",
            "filename": str(LOG_FILE),
            "mode": "w",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": True,
        },
        "__main__": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": True,
        },
        "model.automation": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": True,
        },
        "model.carriers.base": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": True,
        },
        "model.carriers.builders.concept": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": True,
        },
        "model.carriers.builders.kemah": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": True,
        },
        "model.carriers.builders.yachtinsure": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": True,
        },
        "model.doc.filler": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": True,
        },
        "model.doc.parser": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": True,
        },
        "model.web.scraper": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}