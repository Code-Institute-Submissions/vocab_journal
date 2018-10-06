/* global $ */
$(document).ready(function() {
    // $('.collapsible').collapsible();
    // $('select').material_select();
    // $('.button-collapse').sideNav();
    var Ddate = new Date(1984, 11, 24)
    $('.datepicker').pickadate({
        selectMonths: true, // Creates a dropdown to control month
        selectYears: 200, // Creates a dropdown of 15 years to control year,
        today: false,
        defaultDate: Ddate,
        setDefaultDate: true,
        format: 'dd/mm/yyyy',
        yearRange: [1940,2000],
        clear: 'Clear',
        close: 'Ok',
        closeOnSelect: false, // Close upon selecting a date,
        container: undefined, // ex. 'body' will append picker to body
    });
});


// function setDueDate(dateString) {
//     var due_date = Date.parse(dateString);
//     $('#due_date').pickadate('picker').set('select', due_date, { format: 'dd/mm/yyyy' }).trigger('change');
// }