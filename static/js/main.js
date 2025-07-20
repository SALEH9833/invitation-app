// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    
    // --- Logique du formulaire de Nouvelle Invitation ---
    const newInvitationForm = document.querySelector('#new-invitation-form');
    if (newInvitationForm) {
        const guestListContainer = document.getElementById('guest-list');
        const addGuestBtn = document.getElementById('add-guest-btn');
        const guestTemplate = document.getElementById('guest-template');
        const mealCountInput = document.getElementById('nombre_repas');
        const dessertCountInput = document.getElementById('nombre_desserts');
        const lemonadeCountInput = document.getElementById('nombre_limonades');
        const hotDrinkCountInput = document.getElementById('nombre_boissons_chaudes');
        const maxGuests = 4;
        let currentGuestCount = guestListContainer.children.length;

        function updateCountsAndListeners() {
            const guestNameInputs = guestListContainer.querySelectorAll('input[name="nom_invite[]"]');
            let activeGuests = 0;
            guestNameInputs.forEach(input => {
                if (input.value.trim() !== '') {
                    activeGuests++;
                }
                input.removeEventListener('input', updateCountsAndListeners);
                input.addEventListener('input', updateCountsAndListeners);
            });
            mealCountInput.value = activeGuests;
            dessertCountInput.value = activeGuests;
            lemonadeCountInput.value = activeGuests;
            hotDrinkCountInput.value = activeGuests;
        }

        addGuestBtn.addEventListener('click', function() {
            if (currentGuestCount < maxGuests) {
                const newGuestRow = guestTemplate.content.cloneNode(true);
                guestListContainer.appendChild(newGuestRow);
                currentGuestCount++;
                updateCountsAndListeners();
                if (currentGuestCount >= maxGuests) {
                    addGuestBtn.disabled = true;
                    addGuestBtn.textContent = 'Limite atteinte';
                }
            }
        });
        updateCountsAndListeners();
    }

    // --- Interaction pour les boutons de refus (Restaurant) ---
    const refuseForms = document.querySelectorAll('.refuse-form');
    refuseForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const confirmed = confirm('Êtes-vous sûr de vouloir refuser cette invitation ?');
            if (!confirmed) {
                event.preventDefault(); // Annule la soumission du formulaire
            }
        });
    });

});