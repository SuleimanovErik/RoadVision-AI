import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer

logger = logging.getLogger(__name__)


class StreamConsumer(AsyncJsonWebsocketConsumer):
    """
    Браузер подключается к ws://localhost:8000/ws/stream/{session_id}/
    Получает детекции которые Celery пушит через channel layer.
    """

    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        self.group_name = f"stream_{self.session_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info("Browser connected to stream session %s", self.session_id)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info("Browser disconnected from session %s", self.session_id)

    async def receive_json(self, content):
        pass

    # вызывается через group_send из Celery
    async def stream_detection(self, event):
        await self.send_json(event["data"])