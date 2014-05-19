function show_linked(selector) {
    var original_selector = selector;
    selector.hover(
        function() {
            var csrftoken = $.cookie('csrftoken');
            var cont = $(this).children('div.post_quote');
            var link_to = $(this).children('a.link_to_post').html().slice(8);
            var type = '';

            if (link_to[0] == 't')
                type = 'thread';
            else
                type = 'post';

            var id = parseInt(link_to.slice(1));

            var url = '/'+type+'/get/'+id+'/';

            if (!cont.html().length) {
                $.ajax({
                    type:'GET',
                    crossDomain: false,
                    cache: true,
                    url: url,
                    data: {},
                    beforeSend: function(xhr) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    },
                    statusCode: {
                        404: function() {
                            cont.html('NOT FOUND (404)')
                        }
                    },
                    success: function(output) {
                        cont.html(output.answer);
                        selector = $(selector.selector); // Updating selector because new posts can contain new links.

                        // Warning! Recursive call!
                        if (selector.length != original_selector.length) {
                            original_selector.unbind();
                            selector = show_linked(selector);
                        }
                    },
                });
            }

            cont.fadeIn();
        },
        function() {
            var cont = $(this).children('div.post_quote');
            cont.fadeOut();
        }

    );
    return selector;
}


$(document).ready(function() {
    // Full image by click
    $('img.post_img').click(function() {
        var temp = '';
        temp = $(this).attr('src');
        $(this).attr('src', $(this).attr('data-alt_name'));
        $(this).attr('data-alt_name', temp);
    });

    // Show/hide options
    $('#options_button').click(function() {
        $('#options').slideToggle();
    }, function(){
        $("#options").slideToggle();
    });

    // Link to post/thread
    $('span.post_link').click(function() {
        var text_field = $('#id_text');
        if (text_field.length)
            text_field.val(text_field.val()+'>>'+$(this).html().slice(1)+"\n");
    });

    // Show/hide quoted posts/threads
    window.links = $('div.link_to_content')
    window.links = show_linked(window.links);
});
