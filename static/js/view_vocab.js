/* global $ */
$(document).ready(function() {
        $('.tooltipped').tooltip({ delay: 20 });

        $('.dropdown-button').dropdown({
            inDuration: 600,
            outDuration: 225,
            constrainWidth: true, // Does not change width of dropdown to that of the activator
            hover: false, // Activate on hover
            gutter: 0, // Spacing from edge
            belowOrigin: true, // Displays dropdown below the button
            alignment: 'left', // Displays dropdown with edge aligned to the left of button
            stopPropagation: false // Stops event propagation
        });
    
});