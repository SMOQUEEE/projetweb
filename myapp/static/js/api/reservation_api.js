class ReservationAPI {
    static async getAvailableBoxes(dateTime) {
        try {
            const response = await fetch(`/api/boxes/available?datetime=${dateTime}`);
            if (!response.ok) throw new Error('Erreur lors de la récupération des box');
            return await response.json();
        } catch (error) {
            console.error('Erreur API:', error);
            throw error;
        }
    }

    static async createReservation(boxId, dateTime) {
        try {
            const response = await fetch('/api/reservations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    box_id: boxId,
                    datetime: dateTime
                })
            });
            if (!response.ok) throw new Error('Erreur lors de la réservation');
            return await response.json();
        } catch (error) {
            console.error('Erreur API:', error);
            throw error;
        }
    }

    static async cancelReservation(reservationId) {
        const response = await fetch('/api/reservations/cancel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ reservation_id: reservationId })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || "Erreur lors de l'annulation");
        }
        
        return await response.json();
    }
}   