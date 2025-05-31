document.addEventListener('DOMContentLoaded', function () {
    const flash = document.querySelector('.flash-message');
    if (flash) {
        setTimeout(() => {
            flash.style.display = 'none';
        }, 3000);
    }
});