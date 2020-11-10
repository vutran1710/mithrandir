import logging


FORMAT = "%(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.warning("Log set")
