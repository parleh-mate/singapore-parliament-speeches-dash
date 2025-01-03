// assets/scroll.js

document.addEventListener('DOMContentLoaded', function() {
    // Function to handle "Read Less" button clicks
    function handleReadLessClick(event) {
        // Prevent default behavior
        event.preventDefault();
        
        // Find the parent card div
        let cardDiv = event.target.closest('.mb-4');
        if(cardDiv) {
            // Scroll the card into view
            cardDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
    
    // Attach event listeners to all current and future "Read Less" buttons
    document.body.addEventListener('click', function(event) {
        if(event.target && event.target.classList.contains('read-less-button-class')) {
            handleReadLessClick(event);
        }
    });
});
