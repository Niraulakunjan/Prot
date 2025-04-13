// static/js/script.js
document.addEventListener('DOMContentLoaded', function () {
    // Auto-focus the first input field
    const firstInput = document.querySelector('input');
    if (firstInput) firstInput.focus();

    // Fade out messages after 5 seconds
    const messages = document.querySelectorAll('.messages p');
    messages.forEach(msg => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.5s';
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });

    // Form submission animation
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function () {
            const button = form.querySelector('button');
            button.disabled = true;
            button.textContent = 'Processing...';
        });
    }
});