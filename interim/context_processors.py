# interim/context_processors.py
from .models import Message

def unread_messages_count(request):
    if request.user.is_authenticated:
        # On compte les messages reçus par l'utilisateur qui ne sont pas encore lus
        count = Message.objects.filter(destinataire=request.user, lu=False).count()
        return {'unread_messages_count': count}
    return {'unread_messages_count': 0}
def notifications_messages(request):
    if request.user.is_authenticated:
        # On compte les messages dont l'utilisateur est le destinataire et qui ne sont pas lus
        count = Message.objects.filter(destinataire=request.user, lu=False).count()
        return {'unread_messages_count': count}
    return {'unread_messages_count': 0}