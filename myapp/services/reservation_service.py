from datetime import datetime, timedelta
from django.utils import timezone

class ReservationService:
    def get_available_boxes(self, date_time):
        """Retourne la liste des boxes NON réservées pour date_time."""
        from ..models import Box, Reservation
        
        # Vérifier si le créneau est dans le passé
        if date_time < timezone.now():
            return []
            
        # Récupérer toutes les boxes
        all_boxes = Box.objects.all()
        
        # Récupérer les réservations pour ce créneau
        # Utiliser la date exacte pour la comparaison
        reserved_box_ids = Reservation.objects.filter(
            creneau_horaire__year=date_time.year,
            creneau_horaire__month=date_time.month,
            creneau_horaire__day=date_time.day,
            creneau_horaire__hour=date_time.hour,
            creneau_horaire__minute=date_time.minute
        ).values_list('box_id', flat=True)
        
        # Exclure les boxes déjà réservées
        available_boxes = all_boxes.exclude(id__in=reserved_box_ids)
        
        return available_boxes

    def can_make_reservation(self, user, date_time):
        """Vérifie si l'utilisateur peut faire une réservation cette semaine"""
        from ..models import Reservation
        
        # Calculer le début et la fin de la semaine
        start_of_week = date_time - timedelta(days=date_time.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # Compter les réservations de la semaine
        weekly_count = Reservation.objects.filter(
            numero_etudiant=user,
            creneau_horaire__range=[start_of_week, end_of_week]
        ).count()
        
        return weekly_count < 3

    def create_reservation(self, box_id, user_id, date_time):
        """Crée une nouvelle réservation"""
        from ..models import Box, Utilisateur, Reservation
        
        try:
            box = Box.objects.get(id=box_id)
            user = Utilisateur.objects.get(id=user_id)
            
            # Vérifier si la box est déjà réservée
            if Reservation.objects.filter(
                box=box,
                creneau_horaire=date_time
            ).exists():
                raise ValueError("Cette box est déjà réservée pour ce créneau")
            
            # Vérifier si l'utilisateur peut réserver
            if not self.can_make_reservation(user, date_time):
                raise ValueError("Vous avez atteint la limite de réservations pour cette semaine")
            
            reservation = Reservation.objects.create(
                box=box,
                numero_etudiant=user,
                creneau_horaire=date_time
            )
            return reservation
        except (Box.DoesNotExist, Utilisateur.DoesNotExist):
            raise ValueError("Box ou utilisateur non trouvé")