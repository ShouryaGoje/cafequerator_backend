import json
import jwt
from channels.generic.websocket import SyncConsumer
from asgiref.sync import async_to_sync

class QueueConsumer(SyncConsumer):

    def websocket_connect(self,event):
        self.token = self.scope['query_string'].decode().split('=')[-1]
        self.payload = jwt.decode(self.token, 'secret', algorithms=['HS256'])
        self.room_name = f"queue_{self.payload['id']}"
        self.send({
            'type': 'websocket.accept',
        })
        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
            )
        print(f"[{self.channel_name}] - You are connected to room {self.room_name}")

    def websocket_receive(self,event):
        print(f'[{self.channel_name}] - Recieved message - {event.get("text")}')
        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
            'type': 'websocket.message',
            'text': event.get("text")
            }
        )

    def websocket_message(self,event):
        print(f'[{self.channel_name}] - Message Sent - {event.get("text")}')
        self.send({
            'type': 'websocket.send',
            'text': event.get("text")
        })

    def websocket_disconnect(self,event):
        print(f"[{self.channel_name}] - You are disconnected")
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name
            )

    # async def connect(self):
    #     # Extract the ID from the query string
        self.token = self.scope['query_string'].decode().split('=')[-1]
        self.payload = jwt.decode(self.token, 'secret', algorithms=['HS256'])
        self.group_name = f"queue_{self.payload['id']}"  # Group name based on user ID
        
    #     # Add the user to the group
    #     if self.channel_layer:
    #         await self.channel_layer.group_add(
    #             self.group_name,
    #             self.channel_name
    #         )

    #     await self.accept()
    #     await self.send(text_data=json.dumps({
    #         'message': 'added to :'+ str(self.payload['id'])}))

    # async def disconnect(self, code):
    #     # Remove the user from the group
    #     if self.channel_layer:
    #         await self.channel_layer.group_discard(
    #             self.group_name,
    #             self.channel_name
    #         )

    # async def receive_group_message(self, event):
    #     # This method handles messages sent to the group
    #     message = event['message']
    #     await self.accept( )
    #     await self.send(text_data=json.dumps({
    #         'message': message
    #     }))