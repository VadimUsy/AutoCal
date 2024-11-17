document.addEventListener('DOMContentLoaded', () => {
    // AM/PM Toggle Logic
    const amButton = document.getElementById('am');
    const pmButton = document.getElementById('pm');
    const ampmInput = document.getElementById('ampm');

    amButton.addEventListener('click', () => toggleAmPm(amButton, pmButton, 'AM'));
    pmButton.addEventListener('click', () => toggleAmPm(pmButton, amButton, 'PM'));

    function toggleAmPm(selectedButton, otherButton, value) {
        selectedButton.classList.remove('bg-gray-200', 'text-gray-700');
        selectedButton.classList.add('bg-blue-600', 'text-white');
        otherButton.classList.remove('bg-blue-600', 'text-white');
        otherButton.classList.add('bg-gray-200', 'text-gray-700');
        ampmInput.value = value;
    }

    // Input Validation Logic
    const yearInput = document.getElementById('year');
    const monthInput = document.getElementById('month');
    const dayInput = document.getElementById('day');
    const hourInput = document.getElementById('hour');
    const minuteInput = document.getElementById('minute');
    const titleInput = document.getElementById('title');

    // Helper to enforce ranges
    function validateRange(input, min, max) {
        input.addEventListener('input', () => {
            let value = parseInt(input.value, 10);
            if (value < min || value > max || isNaN(value)) {
                input.setCustomValidity(`Value must be between ${min} and ${max}`);
            } else {
                input.setCustomValidity('');
            }
        });

        input.addEventListener('blur', () => {
            let value = parseInt(input.value, 10);
            if (value < min || value > max || isNaN(value)) {
                input.value = '';
            }
        });

        // Ensure only 4 digits can be entered
        if (input === yearInput) {
            input.addEventListener('input', () => {
                if (input.value.length > 4) {
                    input.value = input.value.slice(0, 4);
                }
            });
        }
    }

    validateRange(yearInput, 1000, 9999); // Valid year range
    validateRange(monthInput, 1, 12);    // Months: 1-12
    validateRange(dayInput, 1, 31);      // Days: 1-31
    validateRange(hourInput, 1, 12);     // Hours: 1-12 (for AM/PM format)
    validateRange(minuteInput, 0, 59);   // Minutes: 0-59

    // Title Validation: Ensure it's not empty
    titleInput.addEventListener('input', () => {
        if (titleInput.value.trim() === '') {
            titleInput.setCustomValidity('Event title is required.');
        } else {
            titleInput.setCustomValidity('');
        }
    });
});