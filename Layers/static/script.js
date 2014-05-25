function temp_look(is_nsfw,selector) {

    if (is_nsfw) {
        selector.mouseenter(function() {
            $(this).css('opacity','1.0');
        });

        selector.mouseleave(function() {
            $(this).css('opacity','0');
        });
    } else
        selector.unbind();

}


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
    $('img').click(function() {
        var temp = '';
        temp = $(this).attr('src');
        $(this).attr('src', $(this).attr('data-alt_name'));
        $(this).attr('data-alt_name', temp);
    });

    // NSFW option and it's cookies
    if ($.cookie('nsfw') == 'true') {
        var selector = $('img.post_img');
        selector.css('opacity','0');
        $('#nsfw').attr('checked',true);
        temp_look(true,selector);
    }

    $('#nsfw').change(function() {
        var nsfw = $('#nsfw').is(':checked');
        var selector = $('img.post_img');
        if (nsfw) {
            selector.css('opacity','0');
            $.cookie('nsfw',true,{path: '/'});
            temp_look(true,selector);
        }
        else {
            selector.css('opacity','1.0');
            $.cookie('nsfw',false,{path: '/'});
            temp_look(false,selector);
        }
    });

    // AJAX request for new posts in thread
    $('#refresh').click(function() {
        var csrftoken = $.cookie('csrftoken');
        var thread_id = $('#thread_id').val();
        var board_name =  $('#board_name').val();
        var posts_numb = $('.post').length;

        $.ajax({
            type:'GET',
            crossDomain: false,
            cache: false,
            url: board_name+"thread/update/"+thread_id+'/'+posts_numb,
            data: {},
            beforeSend: function(xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(output) {
                if (output.is_new) {
                    // Animated version
                    var content = "<div class='inv_cont'>"+output.new_threads+"</div>"
                    $('#post_cont').html($('#post_cont').html()+content);
                    $('#post_cont div.inv_cont').last().fadeIn(700)

                    // move to the page's end
                    var url = location.href;
                    location.href = "#bottom_cont";
                    history.replaceState(null, null, url);

                    // make NSFW new pics
                    $('#nsfw').change()

                    // Links
                    window.links = $('div.link_to_content')
                    window.links = show_linked(window.links)
                }
                else {
                    $('#answer').html('Новых постов нет!');
                    $('#answer').slideToggle("slow");
                }
            },
        });
    });


    // send post via ajax
    $('#send-post').click(function() {
        console.log("SOME");
        var csrftoken = $.cookie('csrftoken');
        var thread_id = $('#thread_id').val();
        var board_name =  $('#board_name').val();
        var form = new FormData(document.getElementById('send_form'));
        $.ajax({
            type:'POST',
            crossdomain: false,
            processData: false,
            cache: false,
            contentType: false,
            MimeType: 'multipart/form-data',
            url: board_name+"thread/"+thread_id+'/add_post/',
            data: form,
            beforeSend: function(xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(output) {
                $('#clear').click();
                $('#refresh').click();
                var url = location.href;
                location.href = "#bottom_cont";
                history.replaceState(null, null, url);
                $('#form_table').html(output.form);
            },
        });
    });


    // Show/hide options
    $('#options_button').click(function() {
        $('#options').slideToggle();
    });

    // Link to post/thread
    $('span.post_link').click(function() {
        var text_field = $('#id_text');
        if (text_field.length)
            text_field.val(text_field.val()+'>>'+$(this).html().slice(1)+"\n");
    });


    // Cookie for hiding.
    $('.sage_button').click(function() {
        var thID = $(this).parent().parent().attr("id");
        if ($.cookie(thID) == "true") {
            $.cookie(thID, "false", {path: "/"});
            $(this).parent().parent().children('.post').slideToggle();
        } else {
            $.cookie(thID, "true", {path: "/"});
            $(this).parent().parent().children('.post').slideToggle();
        }
    });

    // Hide thread/s
    $('.thread').each(function () {
        var currID = $(this) .attr('id');
        if ($.cookie(currID) == 'true') {
            $(this) .children('.post').hide();
        }
    });

    // Show/hide quoted posts/threads
    window.links = $('div.link_to_content')
    window.links = show_linked(window.links);
});
