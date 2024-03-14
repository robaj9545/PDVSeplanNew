
# bot.py

import logging
import json
import requests
from django.conf import settings
from .models import Conversation, Attendant

logger = logging.getLogger(__name__)

WHATSAPP_TOKEN = settings.WHATSAPP_TOKEN
VERIFY_TOKEN = settings.VERIFY_TOKEN
TOKEN_GERAL = settings.TOKEN_GERAL


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
        
    def start_conversation_with_attendant(self, attendant):
        # Iniciar uma nova conversa com o atendente
        conversation = Conversation.objects.create(customer=self.customer, attendant=attendant)
        attendant.status = 'OCUPADO'
        attendant.save()
        self.send_whatsapp_message(attendant.phone_number, f"Nova conversa iniciada com {self.customer.name}.")
        self.send_whatsapp_message(self.sender_number, f"Você está agora conversando com {attendant.name}.")

    def end_conversation(self):
        # Finalizar a conversa
        if self.customer and self.customer.conversation_set.exists():
            conversation = self.customer.conversation_set.latest('started_at')
            conversation.delete()
            if conversation.attendant:
                attendant = conversation.attendant
                attendant.status = 'LIVRE'
                attendant.save()
                self.send_whatsapp_message(attendant.phone_number, f"Conversa com {self.customer.name} finalizada.")
            self.send_whatsapp_message(self.sender_number, "A conversa foi finalizada. Obrigado!")
        else:
            self.send_whatsapp_message(self.sender_number, "Você não está em uma conversa.")

    def process_message(self):
        # Processar a mensagem recebida
        if not self.customer.name:
            self.ask_name()
        else:
            if self.message.lower() == 'sair':
                self.end_conversation()
            else:
                self.process_menu()
                
                
    def forward_message_to_attendant(self, message):
        if self.customer and self.customer.conversation_set.exists():
            conversation = self.customer.conversation_set.latest('started_at')
            if conversation.attendant:
                self.send_whatsapp_message(conversation.attendant.phone_number, f"De {self.customer.name}: {message}")
            else:
                self.send_whatsapp_message(self.sender_number, "Atualmente não há atendente disponível.")
        else:
            self.send_whatsapp_message(self.sender_number, "Você não está em uma conversa.")

    def forward_message_to_customer(self, message):
        if self.customer and self.customer.conversation_set.exists():
            conversation = self.customer.conversation_set.latest('started_at')
            self.send_whatsapp_message(self.sender_number, f"De {conversation.attendant.name}: {message}")
        else:
            self.send_whatsapp_message(self.sender_number, "Você não está em uma conversa.")

    def process_message(self):
        # Processar a mensagem recebida
        if not self.customer.name:
            self.ask_name()
        else:
            if self.message.lower() == 'sair':
                self.end_conversation()
            elif self.customer.conversation_set.exists():
                if self.customer.conversation_set.latest('started_at').attendant:
                    self.forward_message_to_attendant(self.message)
                else:
                    self.send_whatsapp_message(self.sender_number, "Aguardando um atendente se conectar.")
            else:
                self.process_menu()

    def process_attendant_message(self):
        # Processar a mensagem do atendente
        if self.customer.conversation_set.exists():
            self.forward_message_to_customer(self.message)
        else:
            self.send_whatsapp_message(self.sender_number, "Você não está em uma conversa.")
            
    def notify_attendant(self):
        # Notificar o atendente quando um cliente inicia uma conversa
        free_attendant = Attendant.objects.filter(status='LIVRE').first()
        if free_attendant:
            self.start_conversation_with_attendant(free_attendant)
        else:
            self.send_whatsapp_message(self.sender_number, "Todos os atendentes estão ocupados. Por favor, aguarde.")

    def forward_message_to_attendant(self, message):
        if self.customer and self.customer.conversation_set.exists():
            conversation = self.customer.conversation_set.latest('started_at')
            if conversation.attendant:
                self.send_whatsapp_message(conversation.attendant.phone_number, f"De {self.customer.name}: {message}")
            else:
                self.send_whatsapp_message(self.sender_number, "Atualmente não há atendente disponível.")
                self.notify_attendant()
        else:
            self.send_whatsapp_message(self.sender_number, "Você não está em uma conversa.")

    def forward_message_to_customer(self, message):
        if self.customer and self.customer.conversation_set.exists():
            conversation = self.customer.conversation_set.latest('started_at')
            self.send_whatsapp_message(self.sender_number, f"De {conversation.attendant.name}: {message}")
        else:
            self.send_whatsapp_message(self.sender_number, "Você não está em uma conversa.")

    def process_message(self):
        if not self.customer.name:
            self.ask_name()
        else:
            if self.message.lower() == 'sair':
                self.end_conversation()
            elif self.customer.conversation_set.exists():
                if self.customer.conversation_set.latest('started_at').attendant:
                    self.forward_message_to_attendant(self.message)
                else:
                    self.send_whatsapp_message(self.sender_number, "Aguardando um atendente se conectar.")
                    self.notify_attendant()
            else:
                self.process_menu()

    def process_attendant_message(self):
        if self.customer.conversation_set.exists():
            self.forward_message_to_customer(self.message)
        else:
            self.send_whatsapp_message(self.sender_number, "Você não está em uma conversa.")