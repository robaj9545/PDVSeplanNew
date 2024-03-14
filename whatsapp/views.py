from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from dotenv import load_dotenv
import logging
import json
import requests
from .models import Customer, Attendant, Conversation

logger = logging.getLogger(__name__)

load_dotenv()

WHATSAPP_TOKEN = settings.WHATSAPP_TOKEN
VERIFY_TOKEN = settings.VERIFY_TOKEN
TOKEN_GERAL = settings.TOKEN_GERAL

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'GET':
        # Lidar com solicitação de verificação
        verify_token = request.GET.get('hub.verify_token')
        if verify_token == VERIFY_TOKEN:
            challenge = request.GET.get('hub.challenge')
            return HttpResponse(challenge)
        else:
            return HttpResponse(status=403)
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info("Dados do webhook recebidos: %s", data)

            for message in data.get('messages', []):
                sender_number = message.get('from')
                incoming_message = message.get('message', {}).get('content', {}).get('text')
                if sender_number and incoming_message:
                    bot = WhatsAppBot(sender_number, incoming_message)
                    bot.process_message()
                else:
                    logger.warning("Formato de mensagem inválido: %s", message)
            
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            logger.exception("Erro ao processar solicitação de webhook: %s", e)
            return JsonResponse({'status': 'error', 'message': 'Erro interno do servidor'}, status=500)
    else:
        return HttpResponse(status=400)

class WhatsAppBot:
    def __init__(self, sender_number, message):
        self.sender_number = sender_number
        self.message = message
        self.customer = self.get_or_create_customer(sender_number)

    def get_or_create_customer(self, phone_number):
        # Obter ou criar cliente com base no número de telefone
        customer, created = Customer.objects.get_or_create(phone_number=phone_number)
        return customer

    def send_whatsapp_message(self, recipient_number, message):
        # Enviar mensagem pelo WhatsApp
        base_url = settings.URL_BASE_DA_API_DO_WHATSAPP
        token = settings.SEU_TOKEN

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "from": f"whatsapp:{self.sender_number}",
            "to": f"whatsapp:{recipient_number}",
            "message": {
                "content": {
                    "text": message
                }
            }
        }

        try:
            response = requests.post(f"{base_url}/v1/messages", json=payload, headers=headers)
            response.raise_for_status()
            logger.info("Mensagem enviada com sucesso para %s", recipient_number)
        except requests.exceptions.RequestException as e:
            logger.error("Erro ao enviar mensagem: %s", e)

    def process_message(self):
        # Processar mensagem recebida
        if not self.customer.name:
            self.ask_name()
        else:
            self.process_menu()

    def ask_name(self):
        # Perguntar o nome do cliente
        message = "Olá! Qual é o seu nome?"
        self.send_whatsapp_message(self.sender_number, message)

    def process_menu(self):
        # Processar opções do menu
        if self.message in ["1", "2", "3"]:
            menu = "1. Enviar comprovante\n2. Falar com um atendente\n3. Sair"
            message = f"Olá {self.customer.name}!\n{menu}"
            self.send_whatsapp_message(self.sender_number, message)

            if self.message == "1":
                self.request_proof()
            elif self.message == "2":
                self.request_attendant()
            elif self.message == "3":
                self.send_whatsapp_message(self.sender_number, "Obrigado por utilizar nossos serviços. Até logo!")
        else:
            self.send_whatsapp_message(self.sender_number, "Opção inválida. Por favor, escolha uma opção válida.")

    def request_proof(self):
        # Solicitar comprovante
        self.send_whatsapp_message(self.sender_number, "Por favor, envie o comprovante.")

    def request_attendant(self):
        # Solicitar atendente disponível
        free_attendant = Attendant.objects.filter(status='LIVRE').first()
        if free_attendant:
            self.start_conversation_with_attendant(free_attendant)
        else:
            self.send_whatsapp_message(self.sender_number, "Todos os atendentes estão ocupados. Por favor, aguarde.")

    def start_conversation_with_attendant(self, attendant):
        # Iniciar conversa com atendente
        conversation = Conversation.objects.create(customer=self.customer, attendant=attendant)
        attendant.status = 'OCUPADO'
        attendant.save()
        self.send_whatsapp_message(attendant.phone_number, f"Nova conversa iniciada com {self.customer.name}.")
        self.send_whatsapp_message(self.sender_number, f"Você está agora conversando com {attendant.name}.")
