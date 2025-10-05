# TODO: Implement logging configuration
import logging
import logging.config
import os
from pathlib import Path

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_FILE = os.getenv("LOG_FILE", "taskflow.log")
LOG_PATH = Path(LOG_DIR)
LOG_PATH.mkdir(exist_ok=True)

LOGGING_CONFIG = {
	"version": 1,
	"disable_existing_loggers": False,
	"formatters": {
		"standard": {
			"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
		},
		"detailed": {
			"format": "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
		}
	},
	"handlers": {
		"console": {
			"class": "logging.StreamHandler",
			"formatter": "standard",
			"level": LOG_LEVEL,
			"stream": "ext://sys.stdout"
		},
		"file": {
			"class": "logging.handlers.RotatingFileHandler",
			"formatter": "detailed",
			"level": LOG_LEVEL,
			"filename": str(LOG_PATH / LOG_FILE),
			"maxBytes": 5 * 1024 * 1024,  # 5MB
			"backupCount": 5,
			"encoding": "utf8"
		}
	},
	"root": {
		"level": LOG_LEVEL,
		"handlers": ["console", "file"]
	},
	"loggers": {
		"uvicorn": {
			"level": "WARNING",
			"handlers": ["console", "file"],
			"propagate": False
		},
		"taskflow": {
			"level": LOG_LEVEL,
			"handlers": ["console", "file"],
			"propagate": False
		}
	}
}

def setup_logging():
	logging.config.dictConfig(LOGGING_CONFIG)

def get_logger(name: str = "taskflow") -> logging.Logger:
	return logging.getLogger(name)