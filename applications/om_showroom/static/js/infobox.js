// Javascript written by Tyler Mulligan
// http://www.detrition.net

$(document).ready(function() {

	// Info box slidedown
	$('.info_header a').click(function () {
		var id=$(this).attr("href")
		$(id+' .info_content').slideToggle('fast');
		$(id+' .info_content p').fadeIn(1200);
		$(id+' .info_content code').fadeIn(1800);
		return false;
    });
	
		
});

// information box
function hide_info(id) {
	$(id).fadeOut("slow");
	$.cookie('pd_'+id.replace("#",""), 'true', { expires: 30, path: '/' } );
}
