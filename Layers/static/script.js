$(document).ready(function() {
    // Create thread via form
    $('#send_thread').click(function() {
        var csrftoken = $.cookie('csrftoken');
        var board_name = $('#board_name').val()
        var form = new FormData(document.getElementById('send_form'));

        $.ajax({
            type:'POST',
            crossDomain: false,
            processData: false,
            cache: false,
            contentType: false,
            MimeType: 'multipart/form-data',
            url: "/"+board_name+"/add_thread",
            data: form,
            beforeSend: function(xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(output) {
                if (output.success == true) {
                    document.location.href = output.url
                } else {
                    $('#form_table').html(output.form)
                }
                //$('#form_table').html(output.form);
            },
        });
    });
});