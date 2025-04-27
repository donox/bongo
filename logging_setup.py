import logging


# Set up logging
logging.basicConfig(
    level=logging.WARN,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("led_controller.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)