/* global $ */
$(document).ready(function() {
    /* global $ */
    var d = new Date();
    $(".current_date").text(d);

    // ADD TAGS TO THE POOL
    $("#addTag").unbind('click').click(function() {

        var tagVal = $("#tag").val();
        var addedTaggs = $("#tag-pool").val();

        // only add tags if it hasnt been added
        if (!addedTaggs.includes(tagVal)) {

            if (addedTaggs === "") {
                // adding to an empty string
                $("#tag-pool").val(`${tagVal}`);
            }
            else {
                // adding to an existing string 
                $("#tag-pool").val(`${addedTaggs}, ${tagVal}`);
            }

            // clear for the next tag to be added
            $("#tag").val("");
        }
    })

    // CLEAR ALL TAGS
    $("#removeTags").unbind('click').click(function() {
        $("#tag").val("");
        $("#tag-pool").val("");
    })

    // disable enter on the form, this will stop incomplete form submissions,  
    $(document).on('keyup keypress', 'form input[type="text"]', function(event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            return false;
        }
    });


});
