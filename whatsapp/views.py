# views.pi
import requests
import json
import os
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import Http404
from itertools import chain
from decimal import Decimal
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from dotenv import load_dotenv


load_dotenv()
# Carrega variáveis de ambiente de .env


# Access tokens for your app
WHATSAPP_TOKEN = settings.WHATSAPP_TOKEN
VERIFY_TOKEN = settings.VERIFY_TOKEN
# Access token for your app
# (copy token from DevX getting started page
# and save it as environment variable into the .env file)


def index(request):
    return HttpResponse("Olá, mundo! Esta é uma resposta HTTP do Django.")
    #return render(request, 'whatsapp/index.html')
    


@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'POST':
        body = json.loads(request.body)

        # Check the Incoming webhook message
        print(json.dumps(body, indent=2))

        # Extract necessary information from the incoming message
        if 'object' in body:
            changes = body.get('entry', [{}])[0].get('changes', [{}])[0]
            if 'messages' in changes.get('value', {}):
                phone_number_id = changes['value']['metadata']['phone_number_id']
                from_number = changes['value']['messages'][0]['from']
                msg_body = changes['value']['messages'][0]['text']['body']

                # Prepare the response message
                response_message = "Ack: " + msg_body

                # Send the response back to the sender
                send_message(phone_number_id, from_number, response_message)

                return JsonResponse({'status': 'success'})

        return JsonResponse({'error': 'Invalid request'}, status=400)

def send_message(phone_number_id, recipient, message):
    url = f"https://graph.facebook.com/v12.0/{phone_number_id}/messages?access_token={WHATSAPP_TOKEN}"
    data = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "text": {"body": message}
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()

@csrf_exempt
def whatsapp_webhook_verification(request):
    verify_token = request.GET.get('hub.verify_token')
    if verify_token == VERIFY_TOKEN:
        challenge = request.GET.get('hub.challenge')
        return HttpResponse(challenge)
    else:
        return HttpResponse(status=403)


