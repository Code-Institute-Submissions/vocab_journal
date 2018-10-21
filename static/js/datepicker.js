/* global $ */
$(document).ready(function() {
    $('.datepicker').pickadate({
        selectMonths: true, // Creates a dropdown to control month
        selectYears: 50, // Creates a dropdown of 15 years to control year,
        today: false,
        setDefaultDate: true,
        format: 'dd/mm/yyyy',
        // yearRange: [1940,2010],
        clear: 'Clear',
        close: 'Ok',
        closeOnSelect: false, // Close upon selecting a date,
        container: undefined, // ex. 'body' will append picker to body
    });

    var $input = $('.datepicker').pickadate()
    // Use the picker object directly.
    var picker = $input.pickadate('picker')
    
    // Using JavaScript Date objects.
    picker.set('select', new Date(1990, 00, 01))
    

    
});


// function setDueDate(dateString) {
//     var due_date = Date.parse(dateString);
//     $('#due_date').pickadate('picker').set('select', due_date, { format: 'dd/mm/yyyy' }).trigger('change');
// }