/**
 * Form validation for event inputs
 */

// Helper to enforce input ranges
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
}

// Limit year input to 4 digits
function limitYearInput(yearInput) {
    yearInput.addEventListener('input', () => {
        if (yearInput.value.length > 4) {
            yearInput.value = yearInput.value.slice(0, 4);
        }
    });
}

// Validate title is not empty
function validateTitle(titleInput) {
    titleInput.addEventListener('input', () => {
        if (titleInput.value.trim() === '') {
            titleInput.setCustomValidity('Event title is required.');
        } else {
            titleInput.setCustomValidity('');
        }
    });
}

// Initialize all form validations
function initializeValidation() {
    const yearInput = document.getElementById('year');
    const monthInput = document.getElementById('month');
    const dayInput = document.getElementById('day');
    const hourInput = document.getElementById('hour');
    const minuteInput = document.getElementById('minute');
    const titleInput = document.getElementById('title');

    if (yearInput) {
        validateRange(yearInput, 1000, 9999);
        limitYearInput(yearInput);
    }
    
    if (monthInput) validateRange(monthInput, 1, 12);
    if (dayInput) validateRange(dayInput, 1, 31);
    if (hourInput) validateRange(hourInput, 1, 12);
    if (minuteInput) validateRange(minuteInput, 0, 59);
    if (titleInput) validateTitle(titleInput);
}

// Export for use in main
export { initializeValidation };
