class Calendar {
    constructor() {
        this.currentDate = new Date();
        this.weekStart = this.getWeekStart(this.currentDate);
        this.isLoading = false;
        this.pendingRequests = new Set();
        this.init();
    }

    init() {
        this.updateWeekDisplay();
        this.generateTimeColumn();
        this.loadTimeSlots();
        this.setupEventListeners();
        this.setupModal();
    }

    getWeekStart(date) {
        const d = new Date(date);
        const day = d.getDay();
        const diff = d.getDate() - day + (day === 0 ? -6 : 1);
        return new Date(d.setDate(diff));
    }

    updateWeekDisplay() {
        const weekStartEl = document.getElementById('weekStart');
        const options = { day: 'numeric', month: 'long', year: 'numeric' };
        weekStartEl.textContent = this.weekStart.toLocaleDateString('fr-FR', options);
    }

    generateTimeColumn() {
        const timeColumn = document.getElementById('timeColumn');
        timeColumn.innerHTML = '';
        
        for (let hour = 8; hour < 20; hour++) {
            const hourSlot = document.createElement('div');
            hourSlot.className = 'time-slot';
            hourSlot.textContent = `${hour.toString().padStart(2, '0')}:00`;
            timeColumn.appendChild(hourSlot);

            const halfHourSlot = document.createElement('div');
            halfHourSlot.className = 'time-slot';
            halfHourSlot.textContent = `${hour.toString().padStart(2, '0')}:45`;
            timeColumn.appendChild(halfHourSlot);
        }
    }

    async loadTimeSlots() {
        if (this.isLoading) return;
        
        try {
            this.isLoading = true;
            const grid = document.getElementById('slotsGrid');
            grid.innerHTML = '';

            for (let hour = 8; hour < 20; hour++) {
                for (let minutes of [0, 45]) {
                    for (let day = 0; day < 6; day++) {
                        const date = new Date(this.weekStart);
                        date.setDate(date.getDate() + day);
                        date.setHours(hour, minutes);
                        
                        const slot = await this.createTimeSlot(date);
                        if (slot) {
                            grid.appendChild(slot);
                        }
                    }
                }
            }
        } finally {
            this.isLoading = false;
        }
    }

    async createTimeSlot(date) {
        const slot = document.createElement('div');
        try {
            const requestId = date.toISOString();

            if (this.pendingRequests.has(requestId)) {
                return null;
            }

            this.pendingRequests.add(requestId);

            const timestamp = new Date().getTime();
            const response = await fetch(`/api/boxes/available?datetime=${date.toISOString()}&_=${timestamp}`);

            this.pendingRequests.delete(requestId);

            if (!response.ok) {
                throw new Error('Erreur lors de la récupération des disponibilités');
            }

            const data = await response.json();
            const availableBoxes = data.available_boxes || [];
            const count = availableBoxes.length;

            slot.className = `time-slot-cell ${this.getAvailabilityClass(count)}`;
            slot.textContent = `${count} box${count > 1 ? 's' : ''} disponible${count > 1 ? 's' : ''}`;
            slot.dataset.date = date.toISOString();
            slot.dataset.boxes = JSON.stringify(availableBoxes);

            const hours = date.getHours().toString().padStart(2, '0');
            const minutes = date.getMinutes().toString().padStart(2, '0');
            slot.dataset.time = `${hours}:${minutes}`;
        } catch (error) {
            console.error('Erreur lors du chargement des disponibilités:', error);
            slot.className = 'time-slot-cell error';
            slot.textContent = 'Erreur';
        }
        return slot;
    }

    async refreshTimeSlots() {
        this.pendingRequests.clear();
        await this.loadTimeSlots();
    }

    async handleBooking(slot, box) {
        const modal = document.getElementById('bookingModal');
        try {
            const response = await ReservationAPI.createReservation(box.id, slot.dataset.date);

            if (response.message) {
                await this.refreshTimeSlots();
                modal.classList.remove('active');
                this.showSuccessMessage('Réservation confirmée ! Un email de confirmation vous a été envoyé.');
            }
        } catch (error) {
            this.showErrorMessage(error.message || 'Erreur lors de la réservation');
        }
    }

    getAvailabilityClass(count) {
        if (count === 0) return 'no-availability';
        if (count >= 4) return 'high-availability';
        return 'medium-availability';
    }

    setupEventListeners() {
        const prevButton = document.querySelector('.prev-week');
        const nextButton = document.querySelector('.next-week');

        prevButton.addEventListener('click', async () => {
            if (this.isLoading) return;
            this.weekStart.setDate(this.weekStart.getDate() - 7);
            this.updateWeekDisplay();
            await this.loadTimeSlots();
        });

        nextButton.addEventListener('click', async () => {
            if (this.isLoading) return;
            this.weekStart.setDate(this.weekStart.getDate() + 7);
            this.updateWeekDisplay();
            await this.loadTimeSlots();
        });

        document.getElementById('slotsGrid').addEventListener('click', (e) => {
            const slot = e.target.closest('.time-slot-cell');
            if (slot && !slot.classList.contains('no-availability')) {
                this.showBookingModal(slot);
            }
        });
    }

    setupModal() {
        const modal = document.getElementById('bookingModal');

        document.querySelector('.cancel-btn').addEventListener('click', () => {
            modal.classList.remove('active');
        });

        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    }

    showBookingModal(slot) {
        const modal = document.getElementById('bookingModal');
        const date = new Date(slot.dataset.date);
        const options = { weekday: 'long', day: 'numeric', month: 'long' };
        const availableBoxes = JSON.parse(slot.dataset.boxes || '[]');

        modal.querySelector('.slot-info').textContent = 
            `${date.toLocaleDateString('fr-FR', options)} à ${slot.dataset.time}`;

        const boxList = document.getElementById('boxList');
        boxList.innerHTML = '';

        availableBoxes.forEach(box => {
            const boxElement = document.createElement('div');
            boxElement.className = 'box-item';
            boxElement.innerHTML = `
                <div class="box-info">
                    <span class="box-name">${box.nom_ufr}</span>
                    <span class="box-status">Disponible</span>
                </div>
                <button class="btn confirm-btn">Réserver</button>
            `;

            boxElement.querySelector('.confirm-btn').addEventListener('click', () => {
                this.handleBooking(slot, box);
            });

            boxList.appendChild(boxElement);
        });

        modal.classList.add('active');
    }

    showSuccessMessage(message) {
        const toast = document.createElement('div');
        toast.className = 'toast success';
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    showErrorMessage(message) {
        const toast = document.createElement('div');
        toast.className = 'toast error';
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new Calendar();
});

document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-btn');
    const reservationApi = new ReservationAPI();

    deleteButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const reservationId = this.dataset.id;
            if (!confirm('Êtes-vous sûr de vouloir annuler cette réservation ?')) {
                return;
            }

            try {
                await reservationApi.cancelReservation(reservationId);
                // Supprimer la carte de réservation
                const card = this.closest('.reservation-card');
                card.remove();
                
                // Mettre à jour les compteurs
                const statsValue = document.querySelector('.stat-value');
                const currentValue = parseInt(statsValue.textContent);
                statsValue.textContent = currentValue - 1;
                
                const remainingValue = document.querySelectorAll('.stat-value')[1];
                remainingValue.textContent = parseInt(remainingValue.textContent) + 1;
                
                // Afficher un message de succès
                alert('Réservation annulée avec succès. Un email de confirmation vous a été envoyé.');
                
                // Si c'était la dernière réservation, afficher le message "Aucune réservation"
                const reservationsList = document.querySelector('.reservations-list');
                if (!reservationsList.querySelector('.reservation-card')) {
                    const noReservationMsg = document.createElement('p');
                    noReservationMsg.textContent = 'Aucune réservation en cours';
                    reservationsList.appendChild(noReservationMsg);
                }
            } catch (error) {
                alert('Erreur lors de l\'annulation : ' + error.message);
            }
        });
    });
});
