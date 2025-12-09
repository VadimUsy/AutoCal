/**
 * Modern AutoCal Frontend
 * Enhanced UX with toast notifications and smooth interactions
 */

import { initializeValidation } from './validation.js';

// Toast notification system
class Toast {
    constructor() {
        this.container = this.createContainer();
    }

    createContainer() {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠'
        };
        
        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.success}</span>
            <span class="toast-message">${message}</span>
        `;
        
        this.container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideInRight 0.4s ease-out reverse';
            setTimeout(() => toast.remove(), 400);
        }, 3000);
    }
}

const toast = new Toast();

// Auto-advance in date/time inputs
function setupAutoAdvance() {
    const inputs = {
        year: { next: 'month', maxLength: 4 },
        month: { next: 'day', maxLength: 2 },
        day: { next: 'hour', maxLength: 2 },
        hour: { next: 'minute', maxLength: 2 },
        minute: { next: 'ampm', maxLength: 2 }
    };

    Object.entries(inputs).forEach(([id, config]) => {
        const input = document.getElementById(id);
        if (!input) return;

        input.addEventListener('input', (e) => {
            const value = e.target.value;
            if (value.length === config.maxLength) {
                const nextInput = document.getElementById(config.next);
                if (nextInput) {
                    setTimeout(() => nextInput.focus(), 50);
                }
            }
        });
    });
}

// Enhanced form submission
function setupFormSubmission() {
    const form = document.querySelector('#eventForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span> Adding...';
        
        // Let form submit naturally, but provide feedback
        setTimeout(() => {
            if (submitBtn.disabled) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        }, 2000);
    });
}

// Handle event removal with confirmation
function setupEventRemoval() {
    const removeForm = document.querySelector('#removeEventsForm');
    if (!removeForm) return;

    removeForm.addEventListener('submit', (e) => {
        const checked = removeForm.querySelectorAll('input[type="checkbox"]:checked');
        
        if (checked.length === 0) {
            e.preventDefault();
            toast.show('Please select events to remove', 'warning');
            return;
        }

        if (!confirm(`Remove ${checked.length} event(s)?`)) {
            e.preventDefault();
            return;
        }

        const submitBtn = removeForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span> Removing...';
    });
}

// Sync to calendar with progress
function setupCalendarSync() {
    const syncBtn = document.querySelector('#syncBtn');
    if (!syncBtn) return;

    syncBtn.addEventListener('click', (e) => {
        const eventCount = document.querySelectorAll('.event-item').length;
        
        if (eventCount === 0) {
            e.preventDefault();
            toast.show('No events to sync', 'warning');
            return;
        }

        if (!confirm(`Sync ${eventCount} event(s) to Google Calendar?`)) {
            e.preventDefault();
            return;
        }

        const originalText = syncBtn.innerHTML;
        syncBtn.disabled = true;
        syncBtn.innerHTML = '<span class="spinner"></span> Syncing...';
        
        // Navigate to sync URL
        const url = syncBtn.dataset.url;
        if (url) {
            window.location.href = url;
        }
    });
}

// Setup logout button
function setupLogout() {
    const logoutBtn = document.querySelector('#logoutBtn');
    if (!logoutBtn) return;

    logoutBtn.addEventListener('click', () => {
        const url = logoutBtn.dataset.url;
        if (url) {
            window.location.href = url;
        }
    });
}

// Check for URL parameters to show toast messages
function checkForMessages() {
    const params = new URLSearchParams(window.location.search);
    const success = params.get('success');
    const error = params.get('error');
    
    if (success) {
        toast.show(decodeURIComponent(success), 'success');
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    if (error) {
        toast.show(decodeURIComponent(error), 'error');
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

// Initialize everything
document.addEventListener('DOMContentLoaded', () => {
    initializeValidation();
    setupAutoAdvance();
    setupFormSubmission();
    setupEventRemoval();
    setupCalendarSync();
    setupLogout();
    checkForMessages();
    
    // Animate elements on load
    document.querySelectorAll('.glass-card').forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
    
    console.log('✨ AutoCal initialized');
});

// Export toast for use in validation
export { toast };
