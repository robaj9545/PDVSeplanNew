from .models import CustomUser

def is_operador(user):
    return hasattr(user, 'customuser') and user.customuser.is_operador()
