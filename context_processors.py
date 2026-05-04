from .models import Message

def notifications_messages(request):
    if request.user.is_authenticated:
        # On utilise le nom exact 'nouveaux_messages_count' que ton template réclame
        count = Message.objects.filter(destinataire=request.user, lu=False).count()
        return {'nouveaux_messages_count': count}
    return {'nouveaux_messages_count': 0}