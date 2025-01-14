from django.core.mail import send_mail
from django.conf import settings
from ..utils.email_utils import get_student_email

class EmailService:
    @staticmethod
    def send_reservation_confirmation(numero_etudiant, box_name, date_time):
        """Envoie un email de confirmation de réservation"""
        email = get_student_email(numero_etudiant)
        subject = 'Confirmation de réservation - Bibliothèque Paris Nanterre'
        message = f"""
        Bonjour,
        
        Votre réservation a été confirmée :
        Box : {box_name}
        Date et heure : {date_time.strftime('%d/%m/%Y à %H:%M')}
        
        Cordialement,
        L'équipe de la Bibliothèque Paris Nanterre
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

    @staticmethod
    def send_cancellation_confirmation(numero_etudiant, box_name, date_time):
        """Envoie un email de confirmation d'annulation de réservation"""
        email = get_student_email(numero_etudiant)
        subject = 'Confirmation d\'annulation - Bibliothèque Paris Nanterre'
        message = f"""
        Bonjour,
        
        L'annulation de votre réservation a été confirmée :
        Box : {box_name}
        Date et heure : {date_time.strftime('%d/%m/%Y à %H:%M')}
        
        Cordialement,
        L'équipe de la Bibliothèque Paris Nanterre
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )