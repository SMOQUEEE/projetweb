document.addEventListener('DOMContentLoaded', function() {
    // Gestion de la suppression des boxes
    document.querySelectorAll('.delete-box').forEach(button => {
        button.addEventListener('click', async function() {
            if (confirm('Êtes-vous sûr de vouloir supprimer cette box ?')) {
                const boxId = this.dataset.id;
                try {
                    const response = await fetch(`/api/boxes/${boxId}/delete`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        }
                    });

                    if (response.ok) {
                        // Supprimer la ligne du tableau
                        this.closest('tr').remove();
                    } else {
                        const data = await response.json();
                        alert(data.error || 'Une erreur est survenue');
                    }
                } catch (error) {
                    console.error('Erreur:', error);
                    alert('Une erreur est survenue lors de la suppression');
                }
            }
        });
    });

    // Gestion de la réservation des boxes
    const reservationModal = document.getElementById('reservationModal');
    const closeButtons = reservationModal.querySelectorAll('.close-button, .btn-secondary');
    
    // Fermer la modal quand on clique sur le bouton de fermeture ou Annuler
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            reservationModal.style.display = 'none';
        });
    });

    // Fermer la modal quand on clique en dehors
    window.addEventListener('click', (e) => {
        if (e.target === reservationModal) {
            reservationModal.style.display = 'none';
        }
    });

    // Gestion du formulaire de réservation
    const reservationForm = document.getElementById('reservationForm');
    reservationForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const boxId = document.getElementById('boxId').value;
        const date = document.getElementById('reservationDate').value;
        const time = document.getElementById('reservationTime').value;
        
        try {
            const response = await fetch('/api/reservations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    box_id: boxId,
                    creneau: `${date}T${time}`
                })
            });

            const data = await response.json();

            if (response.ok) {
                alert('Réservation créée avec succès');
                reservationModal.style.display = 'none';
                location.reload();
            } else {
                alert(data.error || 'Une erreur est survenue');
            }
        } catch (error) {
            console.error('Erreur:', error);
            alert('Une erreur est survenue lors de la réservation');
        }
    });
});