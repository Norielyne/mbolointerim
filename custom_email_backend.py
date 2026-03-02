import ssl
import smtplib
from django.core.mail.backends.smtp import EmailBackend

class CustomEmailBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False
        try:
            # Création d'un contexte SSL totalement permissif
            context = ssl._create_unverified_context()
            
            # On force l'utilisation du contexte SSL dès la création du socket
            if self.use_ssl:
                self.connection = smtplib.SMTP_SSL(
                    self.host, self.port, 
                    timeout=self.timeout, 
                    context=context
                )
            else:
                self.connection = smtplib.SMTP(
                    self.host, self.port, 
                    timeout=self.timeout
                )
                if self.use_tls:
                    self.connection.starttls(context=context)
            
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except:
            if not self.fail_silently:
                raise
            return False