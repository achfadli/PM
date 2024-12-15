// JavaScript for Modern theme can include slider functionality
$(document).ready(function() {
    // Example of a simple slider functionality
    let currentIndex = 0;
    const slides = $('.slider');
    setInterval(function() {
        slides.eq(currentIndex).fadeOut(1000);
        currentIndex = (currentIndex + 1) % slides.length;
        slides.eq(currentIndex).fadeIn(1000);
    }, 3000);
});