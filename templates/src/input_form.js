// event listeners
document.addEventListener('DOMContentLoaded', () => {

    // toggle buttons
    document.querySelectorAll('.toggle-justification, .toggle-suggestion').forEach(button => {
        button.addEventListener('click', function() {
            // find the closest parent .eval-card
            const parentCard = this.closest('.eval-card');
            
            // determine which class to toggle based on the clicked button
            const classToToggle = this.classList.contains('toggle-justification')? '.justification' : '.suggestion'
            const elementToToggle = parentCard.querySelector(classToToggle);
            elementToToggle.style.display = elementToToggle.style.display === 'none' ? 'block' : 'none';
        });
    });

    document.querySelectorAll('.thumb-up-button').forEach(button => {
        button.addEventListener('click', function() {
          // Toggle the "active" class each time the button is clicked
          this.classList.toggle('active');
        // thumbs=up preference
        // todo #3
        });
    });

})