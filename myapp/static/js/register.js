document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registerForm');
    const submitButton = form.querySelector('button[type="submit"]');
    const studentNumberInput = document.getElementById('student_number');
    let isSubmitting = false;
    let lastSubmitTime = 0;
    const SUBMIT_DELAY = 3000; // 3 secondes de délai

    // Fonction pour vérifier si le numéro étudiant existe déjà
    async function checkStudentNumber(numero) {
        try {
            const response = await fetch(`/check-student-number/${numero}/`);
            const data = await response.json();
            return data.exists;
        } catch (error) {
            console.error('Erreur lors de la vérification du numéro étudiant:', error);
            return false;
        }
    }

    // Vérification du numéro étudiant pendant la saisie
    studentNumberInput.addEventListener('input', async function() {
        if (this.value.length === 8) {
            const exists = await checkStudentNumber(this.value);
            if (exists) {
                this.setCustomValidity('Ce numéro étudiant est déjà inscrit');
                this.reportValidity();
            } else {
                this.setCustomValidity('');
            }
        }
    });

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Vérifier si un envoi est déjà en cours
        if (isSubmitting) {
            return;
        }

        // Vérifier le délai entre les soumissions
        const now = Date.now();
        if (now - lastSubmitTime < SUBMIT_DELAY) {
            alert('Veuillez patienter quelques secondes avant de réessayer');
            return;
        }

        // Vérifier si le numéro étudiant existe déjà
        const studentNumber = studentNumberInput.value;
        const exists = await checkStudentNumber(studentNumber);
        if (exists) {
            alert('Ce numéro étudiant est déjà inscrit');
            return;
        }

        // Désactiver le bouton et marquer comme en cours d'envoi
        isSubmitting = true;
        submitButton.disabled = true;
        submitButton.textContent = 'Inscription en cours...';

        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            if (response.redirected) {
                window.location.href = response.url;
            } else {
                const data = await response.json();
                if (data.error) {
                    alert(data.error);
                }
            }
        } catch (error) {
            console.error('Erreur lors de l\'inscription:', error);
            alert('Une erreur est survenue lors de l\'inscription');
        } finally {
            // Réactiver le bouton après le délai
            setTimeout(() => {
                isSubmitting = false;
                submitButton.disabled = false;
                submitButton.textContent = 'S\'inscrire';
                lastSubmitTime = Date.now();
            }, SUBMIT_DELAY);
        }
    });
});