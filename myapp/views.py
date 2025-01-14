from django.shortcuts import render, redirect
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from django.contrib import messages
from .models import Utilisateur, Box, Reservation
from .forms import ConnexionForm
import random
import string
import ssl
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .services.reservation_service import ReservationService
from .services.email_service import EmailService
from datetime import datetime, timedelta
import logging
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt

@require_http_methods(["GET"])
def check_student_number(request, numero):
    exists = Utilisateur.objects.filter(numero_etudiant=numero).exists()
    return JsonResponse({'exists': exists})

def user(request):
    # Récupérer l'utilisateur à partir du numéro étudiant en session
    numero_etudiant = request.session.get('numero_etudiant')
    if not numero_etudiant:
        messages.error(request, "Veuillez vous connecter")
        return redirect('index')
    try:
        # Récupérer l'utilisateur
        utilisateur = Utilisateur.objects.get(numero_etudiant=numero_etudiant)
        
        # Récupérer la semaine demandée ou utiliser la semaine actuelle
        week_param = request.GET.get('week')
        if week_param:
            try:
                start_of_week = datetime.strptime(week_param, '%d/%m/%Y')
            except ValueError:
                start_of_week = datetime.now() - timedelta(days=datetime.now().weekday())
        else:
            start_of_week = datetime.now() - timedelta(days=datetime.now().weekday())
        
        # S'assurer que start_of_week est au début de la journée
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week = start_of_week + timedelta(days=7) - timedelta(microseconds=1)
        
        # Récupérer toutes les réservations futures
        current_time = datetime.now()
        all_reservations = Reservation.objects.filter(
            numero_etudiant=utilisateur,
            creneau_horaire__gte=current_time
        ).order_by('creneau_horaire')
        
        # Récupérer les réservations de la semaine sélectionnée pour le compteur
        reservations_semaine = Reservation.objects.filter(
            numero_etudiant=utilisateur,
            creneau_horaire__range=[start_of_week, end_of_week]
        ).count()
        
        reservations_restantes = 3 - reservations_semaine

        # Ajouter des logs pour le débogage
        logger.info(f"Début de la semaine: {start_of_week}")
        logger.info(f"Fin de la semaine: {end_of_week}")
        logger.info(f"Nombre de réservations cette semaine: {reservations_semaine}")
        logger.info(f"Nombre total de réservations futures: {all_reservations.count()}")

        context = {
            'user': utilisateur,
            'reservations': all_reservations,
            'reservations_semaine': reservations_semaine,
            'reservations_restantes': reservations_restantes,
            'debut_semaine': start_of_week.strftime('%d/%m/%Y'),
            'fin_semaine': end_of_week.strftime('%d/%m/%Y'),
            'today': datetime.now().date()
        }
        
        return render(request, "user.html", context)
        
    except Utilisateur.DoesNotExist:
        messages.error(request, "Utilisateur non trouvé")
        return redirect('index')
    
    
def menu(request):
    return render(request, "menu.html")

def index(request):
    logger.info(f"Méthode de la requête : {request.method}")
    
    if request.method == 'POST':
        numero_etudiant = request.POST.get('numero_etudiant')
        password = request.POST.get('password')
        
        try:
            utilisateur = Utilisateur.objects.get(numero_etudiant=numero_etudiant)
            
            # Vérification directe du mot de passe (non haché)
            if password == utilisateur.mot_de_passe:
                if utilisateur.is_blocked:
                    messages.error(request, "Votre compte est bloqué. Contactez l'administrateur.")
                    return redirect('index')
                    
                request.session['numero_etudiant'] = numero_etudiant
                return redirect('menu')
            else:
                messages.error(request, "Mot de passe incorrect")
        except Utilisateur.DoesNotExist:
            messages.error(request, "Numéro étudiant non trouvé")
        
        return redirect('index')
    
    # Afficher les messages en session
    logger.info(f"Messages en session : {[str(m) for m in messages.get_messages(request)]}")
    return render(request, "index.html")


def generate_password(length=8):
    """Générer un mot de passe aléatoire."""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def send_custom_mail(subject, message, from_email, recipient_list):
    # Créer un contexte SSL personnalisé
    ssl_context = ssl.create_default_context()
    connection = get_connection(
        backend=settings.EMAIL_BACKEND,
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS,
        fail_silently=False,
        ssl_context=ssl_context
    )
    mail = EmailMessage(subject, message, from_email, recipient_list, connection=connection)
    mail.send()

def register(request):
    if request.method == 'POST':
        student_number = request.POST.get('student_number')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        study_year = request.POST.get('study_year')
        
        # Vérifier si l'utilisateur existe déjà
        if Utilisateur.objects.filter(numero_etudiant=student_number).exists():
            messages.error(request, 'Cet utilisateur est déjà inscrit.')
            return redirect('register')
        
        # Générer un mot de passe
        password = generate_password()
        
        # Créer l'email
        email = f"{student_number}@parisnanterre.fr"
        
        # Envoyer l'email
        subject = 'Confirmation d\'inscription - Bibliothèque Paris Nanterre'
        message = f"""
        Bonjour {firstname} {lastname},

        Votre inscription à la bibliothèque de Paris Nanterre a bien été enregistrée.

        Vos identifiants de connexion :
        - Identifiant : {student_number}
        - Mot de passe : {password}

        Nous vous conseillons de changer votre mot de passe lors de votre première connexion.

        Cordialement,
        L'équipe de la bibliothèque
        """
        
        try:
            send_custom_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            
            # Sauvegarder l'utilisateur dans la base de données
            nouvel_utilisateur = Utilisateur(
                numero_etudiant=student_number,
                mot_de_passe=password,
                annee_etude=study_year,
                prenom=firstname,
                nom=lastname,
            )
            nouvel_utilisateur.save()
            
            messages.success(request, 'Inscription réussie ! Vérifiez votre email.')
            return redirect('page_accueil')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'envoi de l\'email : {e}')
            return redirect('register')
            
    return render(request, 'register.html')


def afficher_utilisateurs(request):
    utilisateurs = Utilisateur.objects.all()
    return render(request, 'utilisateurs.html', {'utilisateurs': utilisateurs})






@require_http_methods(["GET"])
def get_available_boxes(request):
    try:
        date_time = datetime.fromisoformat(
            request.GET.get('datetime').replace('Z', '+00:00')
        )
        service = ReservationService()
        available_boxes = service.get_available_boxes(date_time)
        
        return JsonResponse({
            'available_boxes': [
                {'id': box.id, 'nom_ufr': box.nom_ufr}
                for box in available_boxes
            ]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def create_reservation(request):
    try:
        # Récupérer et logger les données brutes
        raw_data = request.body.decode('utf-8')
        logger.info(f"Données brutes reçues : {raw_data}")
        
        # Parser les données JSON
        data = json.loads(raw_data)
        logger.info(f"Données JSON parsées : {data}")
        
        box_id = data.get('box_id')
        # Accepter soit 'creneau' soit 'datetime' comme clé
        creneau = data.get('creneau') or data.get('datetime')
        
        logger.info(f"box_id: {box_id}, creneau: {creneau}")
        
        if not box_id or not creneau:
            logger.warning(f"Données manquantes - box_id: {box_id}, creneau: {creneau}")
            return JsonResponse({
                'error': 'Données manquantes'
            }, status=400)
        
        # Récupérer l'utilisateur connecté
        numero_etudiant = request.session.get('numero_etudiant')
        if not numero_etudiant:
            logger.warning("Utilisateur non authentifié")
            return JsonResponse({
                'error': 'Non authentifié'
            }, status=401)
        
        try:
            utilisateur = Utilisateur.objects.get(numero_etudiant=numero_etudiant)
            box = Box.objects.get(id=box_id)
        except (Utilisateur.DoesNotExist, Box.DoesNotExist) as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur ou de la box : {e}")
            return JsonResponse({
                'error': 'Utilisateur ou box non trouvé'
            }, status=404)
        
        # Convertir le créneau en datetime
        try:
            creneau_dt = datetime.fromisoformat(creneau.replace('Z', '+00:00'))
            logger.info(f"Créneau converti en datetime : {creneau_dt}")
        except ValueError as e:
            logger.error(f"Erreur lors de la conversion du créneau : {e}")
            return JsonResponse({
                'error': 'Format de date invalide'
            }, status=400)
        
        # Vérifier si l'utilisateur a déjà 3 réservations pour la semaine
        debut_semaine = creneau_dt - timedelta(days=creneau_dt.weekday())
        debut_semaine = debut_semaine.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_semaine = debut_semaine + timedelta(days=6)
        
        reservations_semaine = Reservation.objects.filter(
            numero_etudiant=utilisateur,
            creneau_horaire__range=(debut_semaine, fin_semaine)
        ).count()
        
        logger.info(f"Nombre de réservations cette semaine : {reservations_semaine}")
        
        if reservations_semaine >= 3:
            logger.warning(f"Limite de réservations atteinte pour l'utilisateur {numero_etudiant}")
            return JsonResponse({
                'error': 'Vous avez déjà 3 réservations pour cette semaine'
            }, status=400)
        
        # Vérifier si le créneau est déjà réservé
        if Reservation.objects.filter(box=box, creneau_horaire=creneau_dt).exists():
            logger.warning(f"Créneau déjà réservé - box: {box_id}, creneau: {creneau_dt}")
            return JsonResponse({
                'error': 'Ce créneau est déjà réservé'
            }, status=400)
        
        # Créer la réservation
        reservation = Reservation.objects.create(
            numero_etudiant=utilisateur,
            box=box,
            creneau_horaire=creneau_dt
        )
        
        logger.info(f"Réservation créée avec succès - ID: {reservation.id}")
        
        # Envoyer un email de confirmation
        email_etudiant = f"{numero_etudiant}@parisnanterre.fr"
        message = f"""
        Bonjour,
        
        Votre réservation a été confirmée :
        - Box : {box.nom_ufr}
        - Date et heure : {creneau_dt.strftime('%d/%m/%Y à %H:%M')}
        
        Cordialement,
        L'équipe de la bibliothèque Paris Nanterre
        """
        
        try:
            send_mail(
                'Confirmation de réservation',
                message,
                'noreply@bibliotheque.parisnanterre.fr',
                [email_etudiant],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email : {e}")
            # On ne retourne pas d'erreur car la réservation est quand même créée
        
        return JsonResponse({
            'message': 'Réservation créée avec succès',
            'reservation_id': reservation.id
        })
        
    except json.JSONDecodeError as e:
        logger.error(f"Erreur JSON : {e}")
        return JsonResponse({
            'error': 'Données JSON invalides'
        }, status=400)
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la création de la réservation : {e}")
        return JsonResponse({
            'error': str(e)
        }, status=500)


def user_profile(request):
    # Récupérer l'utilisateur à partir du numéro étudiant en session
    numero_etudiant = request.session.get('numero_etudiant')
    if not numero_etudiant:
        return redirect('login')

    try:
        utilisateur = Utilisateur.objects.get(numero_etudiant=numero_etudiant)
        
        # Calculer les dates de la semaine
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        reservations = Reservation.objects.filter(
            numero_etudiant=utilisateur,
            creneau_horaire__range=[start_of_week, end_of_week]
        ).order_by('creneau_horaire')
        
        reservations_semaine = reservations.count()
        reservations_restantes = 3 - reservations_semaine
        
        context = {
            'user': utilisateur,
            'reservations': reservations,
            'reservations_semaine': reservations_semaine,
            'reservations_restantes': reservations_restantes
        }
        
        return render(request, 'user.html', context)
        
    except Utilisateur.DoesNotExist:
        return redirect('login')



@require_http_methods(["POST"])
def cancel_reservation(request):
    try:
        data = json.loads(request.body)
        reservation_id = data.get('reservation_id')
        
        if not reservation_id:
            return JsonResponse({
                'error': 'ID de réservation manquant'
            }, status=400)
        
        numero_etudiant = request.session.get('numero_etudiant')
        if not numero_etudiant:
            return JsonResponse({
                'error': 'Non authentifié'
            }, status=401)
        
        utilisateur = Utilisateur.objects.get(numero_etudiant=numero_etudiant)
        reservation = Reservation.objects.get(id=reservation_id)
        
        # Vérifier que l'utilisateur est autorisé à annuler cette réservation
        if not utilisateur.is_admin and reservation.numero_etudiant.numero_etudiant != numero_etudiant:
            return JsonResponse({
                'error': 'Non autorisé à annuler cette réservation'
            }, status=403)
        
        # Récupérer les informations avant de supprimer
        box_info = reservation.box.nom_ufr
        date_info = reservation.creneau_horaire.strftime('%d/%m/%Y à %H:%M')
        email_etudiant = f"{reservation.numero_etudiant.numero_etudiant}@parisnanterre.fr"
        
        # Supprimer la réservation
        reservation.delete()
        
        # Envoyer un email de confirmation
        message = f"""
        Bonjour,
        
        Votre réservation a été annulée avec succès :
        - Box : {box_info}
        - Date et heure : {date_info}
        
        Cordialement,
        L'équipe de la bibliothèque Paris Nanterre
        """
        
        send_mail(
            'Annulation de votre réservation',
            message,
            'noreply@bibliotheque.parisnanterre.fr',
            [email_etudiant],
            fail_silently=True,
        )
        
        return JsonResponse({
            'message': 'Réservation annulée avec succès',
            'refresh': True  # Indiquer au frontend de rafraîchir la page
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Données JSON invalides'
        }, status=400)
    except Reservation.DoesNotExist:
        return JsonResponse({
            'error': 'Réservation non trouvée'
        }, status=404)
    except Utilisateur.DoesNotExist:
        return JsonResponse({
            'error': 'Utilisateur non trouvé'
        }, status=404)
    except Exception as e:
        logger.error(f"Erreur lors de l'annulation de la réservation : {e}")
        return JsonResponse({
            'error': 'Une erreur est survenue'
        }, status=500)


def delete_reservation(request, reservation_id):
    try:
        reservation = Reservation.objects.get(id=reservation_id)
        reservation.delete()
        return JsonResponse({'status': 'success'})
    except Reservation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Réservation non trouvée'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

from django.contrib.auth import update_session_auth_hash



@csrf_exempt
@require_http_methods(["POST"])
def change_password(request):
    try:
        # Log les données brutes
        raw_data = request.body.decode('utf-8')
        logger.info(f"Données brutes reçues : {raw_data}")
        
        # Parser les données JSON
        data = json.loads(raw_data)
        logger.info(f"Données JSON parsées : {data}")
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        logger.info("Vérification des données reçues")
        if not current_password or not new_password:
            logger.warning("Mot de passe actuel ou nouveau mot de passe manquant")
            return JsonResponse({
                'status': 'error',
                'message': 'Veuillez fournir le mot de passe actuel et le nouveau mot de passe'
            }, status=400)
        
        # Récupérer l'utilisateur connecté
        numero_etudiant = request.session.get('numero_etudiant')
        if not numero_etudiant:
            logger.warning("Utilisateur non authentifié")
            return JsonResponse({
                'status': 'error',
                'message': 'Non authentifié'
            }, status=401)
        
        try:
            utilisateur = Utilisateur.objects.get(numero_etudiant=numero_etudiant)
            logger.info(f"Utilisateur trouvé : {utilisateur.numero_etudiant}")
            
            # Vérifier le mot de passe actuel (supporte les deux formats)
            password_correct = (
                current_password == utilisateur.mot_de_passe or  # Pour les mots de passe non hachés
                check_password(current_password, utilisateur.mot_de_passe)  # Pour les mots de passe hachés
            )
            
            if not password_correct:
                logger.warning("Mot de passe actuel incorrect")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Mot de passe actuel incorrect'
                }, status=400)
            
            # Mettre à jour le mot de passe (sans hachage pour l'instant)
            utilisateur.mot_de_passe = new_password
            utilisateur.save()
            
            logger.info("Mot de passe mis à jour avec succès")
            return JsonResponse({
                'status': 'success',
                'message': 'Mot de passe modifié avec succès'
            })
            
        except Utilisateur.DoesNotExist:
            logger.error(f"Utilisateur non trouvé : {numero_etudiant}")
            return JsonResponse({
                'status': 'error',
                'message': 'Utilisateur non trouvé'
            }, status=404)
            
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de décodage JSON : {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Format de données invalide'
        }, status=400)
    except Exception as e:
        logger.error(f"Erreur inattendue : {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Une erreur est survenue'
        }, status=500)


def admin_dashboard(request):
    # Vérifier si l'utilisateur est admin
    numero_etudiant = request.session.get('numero_etudiant')
    if not numero_etudiant:
        return redirect('index')
    
    try:
        utilisateur = Utilisateur.objects.get(numero_etudiant=numero_etudiant)
        if not utilisateur.is_admin:
            messages.error(request, "Accès non autorisé")
            return redirect('menu')
            
        context = {
            'total_reservations': Reservation.objects.count(),
            'total_users': Utilisateur.objects.count(),
            'available_boxes': Box.objects.count(),
            'recent_reservations': Reservation.objects.order_by('-creneau_horaire')[:5]
        }
        return render(request, 'administrator/dashboard.html', context)
    except Utilisateur.DoesNotExist:
        return redirect('index')

def admin_users(request):
    # Vérifier si l'utilisateur est admin
    numero_etudiant = request.session.get('numero_etudiant')
    if not numero_etudiant:
        return redirect('index')
    
    try:
        utilisateur = Utilisateur.objects.get(numero_etudiant=numero_etudiant)
        if not utilisateur.is_admin:
            return redirect('index')
        
        # Récupérer tous les utilisateurs sauf l'admin actuel
        users = Utilisateur.objects.exclude(numero_etudiant=numero_etudiant).order_by('numero_etudiant')
        
        # Pour chaque utilisateur, récupérer ses réservations futures
        user_data = []
        for user in users:
            reservations = Reservation.objects.filter(
                numero_etudiant=user,
                creneau_horaire__gte=datetime.now()
            ).order_by('creneau_horaire')
            
            user_data.append({
                'user': user,
                'reservations': reservations,
                'total_reservations': reservations.count()
            })
        
        return render(request, 'administrator/users.html', {
            'user_data': user_data
        })
        
    except Utilisateur.DoesNotExist:
        return redirect('index')

@login_required
def boxes(request):
    if not request.session.get('is_admin', False):
        messages.error(request, "Accès non autorisé")
        return redirect('menu')
        
    boxes = Box.objects.all().order_by('nom_ufr')  # Utiliser nom_ufr au lieu de numero
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            nom_ufr = request.POST.get('numero')  # Le champ s'appelle toujours 'numero' dans le formulaire
            try:
                Box.objects.create(nom_ufr=nom_ufr)
                messages.success(request, f"Box {nom_ufr} ajoutée avec succès")
            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout de la box: {str(e)}")
                
        elif action == 'delete':
            box_id = request.POST.get('box_id')
            try:
                box = Box.objects.get(id=box_id)
                box.delete()
                messages.success(request, f"Box {box.nom_ufr} supprimée avec succès")
            except Box.DoesNotExist:
                messages.error(request, "Box non trouvée")
            except Exception as e:
                messages.error(request, f"Erreur lors de la suppression de la box: {str(e)}")
    
    return render(request, 'administrator/boxes.html', {'boxes': boxes})

def admin_boxes(request):
    # Vérifier si l'utilisateur est admin
    numero_etudiant = request.session.get('numero_etudiant')
    if not numero_etudiant:
        return redirect('index')
        
    try:
        utilisateur = Utilisateur.objects.get(numero_etudiant=numero_etudiant)
        if not utilisateur.is_admin:
            messages.error(request, "Accès non autorisé")
            return redirect('menu')
            
        boxes = Box.objects.all().order_by('nom_ufr')
        
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'add':
                nom_ufr = request.POST.get('nom_ufr')
                try:
                    Box.objects.create(nom_ufr=nom_ufr)
                    messages.success(request, f"Box {nom_ufr} ajoutée avec succès")
                except Exception as e:
                    messages.error(request, f"Erreur lors de l'ajout de la box: {str(e)}")
                    
            elif action == 'delete':
                box_id = request.POST.get('box_id')
                try:
                    box = Box.objects.get(id=box_id)
                    box.delete()
                    messages.success(request, f"Box {box.nom_ufr} supprimée avec succès")
                except Box.DoesNotExist:
                    messages.error(request, "Box non trouvée")
                except Exception as e:
                    messages.error(request, f"Erreur lors de la suppression de la box: {str(e)}")
        
        return render(request, 'administrator/boxes.html', {'boxes': boxes})
        
    except Utilisateur.DoesNotExist:
        return redirect('index')

def admin_reservations(request):
    # Vérifier si l'utilisateur est admin
    numero_etudiant = request.session.get('numero_etudiant')
    if not numero_etudiant:
        return redirect('index')
    
    try:
        utilisateur = Utilisateur.objects.get(numero_etudiant=numero_etudiant)
        if not utilisateur.is_admin:
            messages.error(request, "Accès non autorisé")
            return redirect('menu')
            
        reservations = Reservation.objects.all().order_by('-creneau_horaire')
        return render(request, 'administrator/reservations.html', {'reservations': reservations})
    except Utilisateur.DoesNotExist:
        return redirect('index')

@require_http_methods(["POST"])
def toggle_user_block(request, numero_etudiant):
    try:
        # Vérifier si l'utilisateur est admin
        admin_numero = request.session.get('numero_etudiant')
        if not admin_numero:
            return JsonResponse({'status': 'error', 'message': 'Non authentifié'}, status=401)
        
        admin = Utilisateur.objects.get(numero_etudiant=admin_numero)
        if not admin.is_admin:
            return JsonResponse({'status': 'error', 'message': 'Non autorisé'}, status=403)
        
        # Trouver l'utilisateur à bloquer/débloquer
        user = Utilisateur.objects.get(numero_etudiant=numero_etudiant)
        
        # Ne pas permettre de bloquer un admin
        if user.is_admin:
            return JsonResponse({
                'status': 'error',
                'message': 'Impossible de bloquer un administrateur'
            }, status=403)
        
        # Inverser le statut de blocage
        user.is_blocked = not user.is_blocked
        user.save()
        
        return JsonResponse({
            'status': 'success',
            'is_blocked': user.is_blocked,
            'message': 'Utilisateur bloqué' if user.is_blocked else 'Utilisateur débloqué'
        })
        
    except Utilisateur.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Utilisateur non trouvé'
        }, status=404)
    except Exception as e:
        logger.error(f"Erreur lors du blocage/déblocage de l'utilisateur: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Une erreur est survenue'
        }, status=500)


def logout(request):
    # Supprimer toutes les données de session
    request.session.flush()
    messages.success(request, "Vous avez été déconnecté avec succès")
    return redirect('index')


@require_http_methods(["POST"])
def reset_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            numero_etudiant = data.get('numero_etudiant')
            
            try:
                utilisateur = Utilisateur.objects.get(numero_etudiant=numero_etudiant)
                
                # Générer un nouveau mot de passe
                nouveau_mot_de_passe = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                
                # Sauvegarder le nouveau mot de passe (non haché)
                utilisateur.mot_de_passe = nouveau_mot_de_passe
                utilisateur.save()
                
                # Envoyer le mot de passe par email
                email = f"{numero_etudiant}@parisnanterre.fr"
                subject = "Réinitialisation de votre mot de passe - Bibliothèque Paris Nanterre"
                message = f"""Bonjour,
                
Votre mot de passe a été réinitialisé.
Voici votre nouveau mot de passe : {nouveau_mot_de_passe}

Cordialement,
L'équipe de la Bibliothèque Paris Nanterre"""
                
                send_custom_mail(subject, message, settings.EMAIL_HOST_USER, [email])
                
                return JsonResponse({'message': 'Nouveau mot de passe envoyé par email'})
                
            except Utilisateur.DoesNotExist:
                return JsonResponse({'error': 'Numéro étudiant non trouvé'}, status=404)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Données invalides'}, status=400)
            
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)