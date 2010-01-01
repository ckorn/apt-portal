// Javascript written by Tyler Mulligan
// http://www.detrition.net

// Load shadowbox skin
Shadowbox.loadSkin('classic', '/js/skin'); // use the "classic" skin

$(document).ready(function() {
	// Info Box
	
	// How to Install
	if (window.location.hash!="#how_to_install") {	
		$('#how_to_install .info_content').hide();
		$('#how_to_install .info_content p').hide();
		$('#how_to_install .info_content code').hide();
		$('#how_to_install .info_header h2 a').text("Click here to learn how to install games from PlayDeb");

		// Cookie to determine showing of info
		
		// If the cookie is set, hide the welcome messages
		if($.cookie('pd_how_to_install')=='true') {
			$('#how_to_install').hide();
			$('#hide_install').hide();
		// Null or the user wants to see it again
		} else if ($.cookie('pd_to_install')=='false') {
			//show_info();
		}

	}

	// Genre Dropdown
	$('#genre li').hover(
		function(){ $('ul', this).fadeIn('fast'); }, 
		function() { } 
	);
	if (document.all) {
		$('#genre li').hoverClass ('sfHover');
	}
	
	// Shadowbox
	var options = {
        resizeLgImages:     true,
        displayNav:         true,
        handleUnsupported:  'remove',
        enableKeys:			true
    };

    Shadowbox.init(options);
	
	// Ratings
	$('.the_stars :radio.star').rating(); 
	
	// Tags
	$('.add_tag').hide();
	$('.add_new_tag').click(function () { 
		$(this).parent().children('.add_tag').fadeIn();
		return false;
    });
	$('.add_tag_submit').click(function () {
		//$(this).parent('.tags_container').children('.tags').fadeOut();
		$(this).parent().parent('.tags_container').children('.tags').fadeOut();
		$(this).parent().fadeOut();
		// Database requery - then:
		var newtag = $(this).parent().children('.add_tag_box').val()
		if (newtag=="") { newtag="new tag!" }
		$(this).parent().parent('.tags_container').children('.tags').append(", " + newtag );
		$(this).parent().parent('.tags_container').children('.tags').fadeIn();
	});

	// User Action Click Cookie
	$("#hide_install").click(function(e){
		// Kept incase of future changes
		/* if($.cookie('pd_to_install')=='true') {
			//show_weclome();
		} else if ($.cookie('pd_to_install')==null || $.cookie('pd_to_install')=='false') {
			//hide_info();
		} */		
		hide_info("#how_to_install");
	});

	/* Set the cookie for the selected release */
	$(".release_set").click(function(e){
		var currentId = $(this).attr('id'); 
		var release = currentId.replace('release_', '');
		$.cookie('release', release, { path: '/', expires: 30 }); 		
	});
	
});

// Dropdown Function
$.fn.hoverClass = function(c) {
	return this.each(function(){
		$(this).hover( 
			function() { $(this).addClass(c);  },
			function() { $(this).removeClass(c); }
		);
	});
};

// Vertically-center thumbnails
$(window).load(function(){
	$('.game .thumb').each(function(){
		var imageheight = $(this).height();
		var margin = (209-imageheight)/2;
		$(this).css('margin-top',margin-5); // -5 because there's 5px to the top
	});
});
