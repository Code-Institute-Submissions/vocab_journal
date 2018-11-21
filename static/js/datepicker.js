/* global $ */
$(document).ready(function() {
    $('.datepicker').pickadate({
        selectMonths: true, // Creates a dropdown to control month
        selectYears: 50, // Creates a dropdown of 15 years to control year,
        today: false,
        setDefaultDate: true,
        format: 'yyyy/mm/dd',
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
