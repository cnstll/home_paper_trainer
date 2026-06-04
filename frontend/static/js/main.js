// Main JavaScript file for Home Paper Trainer

// Initialize HTMX extensions (if needed)
htmx.logAll();

// Global error handler
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
});

// Document ready
htmx.onLoad(function(content) {
    console.log('HTMX content loaded');
    
    // Add fade-in class to all elements with data-fade-in attribute
    document.querySelectorAll('[data-fade-in]').forEach((el) => {
        el.classList.add('fade-in');
    });
});

// Utility functions
const Utils = {
    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Format date
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },
    
    // Show notification
    showNotification(message, type = 'info') {
        const colors = {
            info: 'bg-blue-500',
            success: 'bg-green-500',
            warning: 'bg-yellow-500',
            error: 'bg-red-500'
        };
        
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 px-4 py-2 text-white rounded-lg shadow-lg ${colors[type]} z-50`;
        notification.innerHTML = message;
        notification.id = 'notification';
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Utils;
}
