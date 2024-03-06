from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from dotenv import load_dotenv
import requests
import json

load_dotenv()

WHATSAPP_TOKEN = settings.WHATSAPP_TOKEN
VERIFY_TOKEN = settings.VERIFY_TOKEN

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'GET':
        # Handle verification request
        verify_token = request.GET.get('hub.verify_token')
        if verify_token == VERIFY_TOKEN:
            challenge = request.GET.get('hub.challenge')
            return HttpResponse(challenge)
        else:
            return HttpResponse(status=403)
    elif request.method == 'POST':
        # Handle incoming messages
        data = json.loads(request.body.decode('utf-8'))
        for entry in data['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    sender_id = message['sender']['id']
                    message_text = message['message']['text']
                    send_message(sender_id, "Robô robertinho: Olá meu dono saiu e estou aqui para lhe atender, obrigado por mandar uma mensagem, logo te respondo.")
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)

def send_message(recipient_id, message_text):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WHATSAPP_TOKEN}',
    }
    data = {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': message_text
        }
    }
    response = requests.post('https://graph.facebook.com/v12.0/me/messages', headers=headers, json=data)
    print(response.json())  # Print the response for debugging purposes
