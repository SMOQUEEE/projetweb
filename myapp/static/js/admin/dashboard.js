document.addEventListener('DOMContentLoaded', function() {
    // Initialiser le graphique des statistiques
    const ctx = document.getElementById('stats-chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'],
            datasets: [{
                label: 'Réservations',
                data: [12, 19, 15, 17, 14, 8],
                borderColor: '#2196f3',
                backgroundColor: 'rgba(33, 150, 243, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Réservations par jour'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });

    // Gestionnaire de recherche
    const searchInput = document.querySelector('.search-input');
    const searchButton = searchInput.nextElementSibling;
    
    searchButton.addEventListener('click', function() {
        const searchTerm = searchInput.value.toLowerCase();
        const tableRows = document.querySelectorAll('.admin-table tbody tr');
        
        tableRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });

    // Gestionnaire de filtres
    const filterSelects = document.querySelectorAll('.filter-select');
    const applyFilterButton = document.querySelector('.filters .btn-primary');
    
    applyFilterButton.addEventListener('click', function() {
        const timeFrame = filterSelects[0].value;
        const boxFilter = filterSelects[1].value;
        
        // Ici, vous pouvez ajouter la logique pour mettre à jour le graphique
        // en fonction des filtres sélectionnés
        console.log('Filtres appliqués:', { timeFrame, boxFilter });
    });

    // Animation des cartes de statistiques
    const statNumbers = document.querySelectorAll('.stat-number');
    
    statNumbers.forEach(stat => {
        const finalValue = parseInt(stat.textContent);
        let currentValue = 0;
        const duration = 1000; // 1 seconde
        const steps = 20;
        const increment = finalValue / steps;
        const stepDuration = duration / steps;
        
        const counter = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                stat.textContent = finalValue;
                clearInterval(counter);
            } else {
                stat.textContent = Math.floor(currentValue);
            }
        }, stepDuration);
    });

    // Gestionnaire des boutons d'action
    const actionButtons = document.querySelectorAll('.action-buttons .btn');
    
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const action = this.textContent.toLowerCase();
            const row = this.closest('tr');
            const reservationId = row.dataset.id;
            
            if (action === 'annuler') {
                if (confirm('Êtes-vous sûr de vouloir annuler cette réservation ?')) {
                    // Ici, vous pouvez ajouter la logique pour annuler la réservation
                    console.log('Annulation de la réservation:', reservationId);
                    row.style.opacity = '0.5';
                }
            }
        });
    });
});
