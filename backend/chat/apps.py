from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'

    def ready(self):
        try:
            # Import and initialize services only when not running migrations
            from django.db import connection
            if connection.connection is not None:
                
                logger.info("Initializing services...")
                logger.info("Services initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing services: {str(e)}")
