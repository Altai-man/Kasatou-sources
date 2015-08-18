function temp_look(is_nsfw, selector) {
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

function cens_look(is_cens, selector) {
    if (is_cens) {
	selector.mouseenter(function() {
	    $(this).css('opacity','1.0');
	    $(this).css('background-color','#ffffff');
	});

	selector.mouseleave(function() {
	    $(this).css('opacity','0');
	});
    } else
	selector.unbind();
}


function deleteAndHide(id, csrftoken) {
    $.ajax({
	type:'POST',
	crossDomain: false,
	cache: false,
	url: "post_deleting" +'/' + id.slice(3),
	data: {},
	beforeSend: function(xhr) {
	    xhr.setRequestHeader("X-CSRFToken", csrftoken);
	},
	success: function(output) {
	    $("#" + id).parent().parent().parent().hide();
	},
	error: function (xhr, textStatus, errorThrown) {
	    if (errorThrown === "BAD REQUEST") {
		alert("Post with this number doesn't exist.")
	    } else if (errorThrown === "FORBIDDEN") {
		alert("You don't have enough rights to do so.");
	    }
	}
    });
};

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
	var selector = $('div.post-images');
	selector.css('opacity','0');
	$('#nsfw_btn').attr('checked',true);
	temp_look(true,selector);
    }

    $('#nsfw_btn').change(function() {
	var nsfw = $('#nsfw').is(':checked');
	var selector = $('div.post-images');
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

    // cens option and it's cookies
    if ($.cookie('cens') == 'true') {
	var selector = $('.censored');
	selector.css('opacity','0');
	$('#cens_btn').attr('checked',true);
	cens_look(true,selector);
    }

    $('#cens_btn').change(function() {
	var cens = $('#cens_btn').is(':checked');
	var selector = $('.censored');
	if (cens) {
	    selector.css('opacity','0');
	    $(this).css('background-color','#ffffff');
	    $.cookie('cens',true,{path: '/'});
	    cens_look(true,selector);
	}
	else {
	    selector.css('opacity','1.0');
	    $(this).css('background-color','#000000');
	    $.cookie('cens',false,{path: '/'});
	    cens_look(false,selector);
	}
    });




    $('.delete_btn').click(function() {
	var id = this.id;
	var csrftoken = $.cookie('csrftoken');
	deleteAndHide(id, csrftoken);
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
		$("#errors").html("");
	    },
	    error: function(output) {
		$("#errors").html(output.responseText + "<br>");
	    }
	});
    });


    // Show/hide options
    $('#options_button').click(function() {
	$('#options').slideToggle();
    });

    // Link to post/thread
    $('span.post_link').click(function() {
	if (document.URL.indexOf("thread") !== -1) {
	    $('#mainform').insertAfter($(this).parent().parent());
	    $('#mainform').css("margin", "0 auto 15pt 40pt");
	    var text_field = $('#id_text');
	    if (text_field.length)
		text_field.val(text_field.val()+'>>'+$(this).html().slice(1)+"\n");
    }});

    // Form hiding.
    $('#form-button').click(function() {
	$('#mainform').slideToggle();
    })

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


    // markdown buttons
    function wrapText(openTag, closeTag) {
	var textArea = $('#id_text');
	var len = textArea.val().length;
	var start = textArea[0].selectionStart;
	var end = textArea[0].selectionEnd;
	var selectedText = textArea.val().substring(start, end);
	var replacement = openTag + selectedText + closeTag;
	textArea.val(textArea.val().substring(0, start) + replacement + textArea.val().substring(end, len));
    }

    $('#q').click(function () {
	var textArea = $('#id_text');
	var len = textArea.val().length;
	var start = textArea[0].selectionStart;
	var end = textArea[0].selectionEnd;
	var selectedText = textArea.val().substring(start, end);
	var replacement = ">" + selectedText;
	textArea.val(textArea.val().substring(0, start) + replacement + textArea.val().substring(end, len));
    });

    $('#b').click(function () {
	wrapText('**', '**');
    });

    $('#i').click(function () {
	wrapText('*', '*');
    });

    $('#s').click(function () {
	wrapText('[s]', '[/s]');
    });

    $('#sp').click(function () {
	wrapText('%%', '%%');
    });

    $('#magic').click(function () {
	wrapText('[m]', '[/m]');
    });

    $('#cd').click(function () {
	wrapText('[code]', '[/code]');
    });

    $('#cens').click(function () {
	wrapText('[cens]', '[/cens]');
    });

    $('#clear').click(function () {
	var textArea = $('#id_text');
  textArea.val("");
    });
});
