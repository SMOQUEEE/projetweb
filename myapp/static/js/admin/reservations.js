document.addEventListener('DOMContentLoaded', () => {
    const deleteButtons = document.querySelectorAll('.delete-reservation');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', async () => {
            if (!confirm('Voulez-vous vraiment supprimer cette réservation ?')) {
                return;
            }

            const reservationId = button.dataset.id;
            try {
                const response = await fetch(`/admin/reservations/${reservationId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });

                if (response.ok) {
                    button.closest('tr').remove();
                } else {
                    alert('Erreur lors de la suppression');
                }
            } catch (error) {
                console.error('Erreur:', error);
                alert('Erreur lors de la suppression');
            }
        });
    });
});