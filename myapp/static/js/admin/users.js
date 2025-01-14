document.addEventListener('DOMContentLoaded', () => {
    const toggleButtons = document.querySelectorAll('.toggle-block');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const userId = button.dataset.id;
            try {
                const response = await fetch(`/admin/users/${userId}/toggle-block/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    const row = button.closest('tr');
                    const statusBadge = row.querySelector('.status-badge');
                    
                    if (data.is_blocked) {
                        statusBadge.textContent = 'Bloqué';
                        statusBadge.classList.add('blocked');
                        button.textContent = 'Débloquer';
                    } else {
                        statusBadge.textContent = 'Actif';
                        statusBadge.classList.remove('blocked');
                        button.textContent = 'Bloquer';
                    }
                } else {
                    alert('Erreur lors de la modification du statut');
                }
            } catch (error) {
                console.error('Erreur:', error);
                alert('Erreur lors de la modification du statut');
            }
        });
    });
});