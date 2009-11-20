
/* screenshot upload button */
$(document).ready(function(){
	var button = $('#upload_button'), interval;
	new AjaxUpload(button,{		
		action: '/appinfo/upload_screenshot', 
		name: 'userfile',
		onSubmit : function(file, ext){
						
			if (ext != 'png') {
				//$('#upload_status_msg').addClass("error_msg");
				alert(str_only_png_error);
				return false;
			}			
			$('#upload_status_msg').removeClass("error_msg");
			$('#upload_status_msg').html('Uploading ' + file);
						
			// change button text, when user selects file			
			button.text('${_("Uploading")}');
			
			// If you want to allow uploading only 1 file at time,
			// you can disable upload button
			this.disable();
			
			// Uploding -> Uploading. -> Uploading...
			interval = window.setInterval(function(){
				var text = button.text();
				if (text.length < 13){
					button.text(text + '.');					
				} else {
					button.text(str_uploading);				
				}
			}, 200);
		},
		onComplete: function(file, response){
			button.text(str_upload);
						
			window.clearInterval(interval);
						
			// enable upload button
			this.enable();			
			$('#upload_status_msg').html('');
			$('img#sreenshot_thumb').attr('src', response+"?"+Math.random());
		}
	});
});

/* form validation */	
$(document).ready(function(){
	$("#applicationForm").validate({
		rules: {
			password1: {
				required: true,
				minlength: 5
			},
			password2: {
				required: true,
				minlength: 5,
				equalTo: "#rpassword1"
			}
		},
		messages: {
			password1: {
				required: "Please provide a password",
				minlength: "At least 5 characters long"
			},
			password2: {
				required: "Please provide a password",
				minlength: "At least 5 characters long",
				equalTo: "Same password as the first"
			},
		}
	});
});	

// prepare the form when the DOM is ready 
$(document).ready(function() { 
    var options = { 
        beforeSubmit:  showRequest,  // pre-submit callback 
        success:       showResponse, // post-submit callback 
		datatype:      'xml'
    }; 
 
    // bind form using 'ajaxForm' 
    $('#applicationForm').ajaxForm(options); 
}); 
 
// pre-submit callback 
function showRequest(formData, jqForm, options) { 
	
	if(! $("#applicationForm").valid() )
		return false;
		
	cat_val = $("#category").val();
	if ( cat_val == '0' || cat_val == 'add' || cat_val == 'del') {
		alert('You must select a category!');
		return false;
	}
	$("#update_status").html('Updating...');
/*
    var queryString = $.param(formData); 
    alert('About to submit: \n\n' + queryString); 
*/
    return true; 
} ;
 
/* post-submit callback  */
function showResponse(responseText, statusText)  {  
    //alert('status: ' + statusText + '\n\nresponseText: \n' + responseText + 
	//        '\n\nThe output div should have already been updated with the responseText.'); 
	var status_msg = "Unknown"
	var mySplitResult = responseText.split(" ", 2);
	var status = mySplitResult[0];	
	var id = mySplitResult[1];
	if(status == 'OK') {
		status_msg = str_update_was_successful;	
		$("#app_id").val(id);
	}
	else
		status_msg = responseText;
	$("#update_status").html(status_msg);
};

/******  Create category window code ******/
$(document).ready(function(){
	
	
	$("#new_category_section").hide("fast");
	$("#category").change(function(){
		if (this.value == 'add') {		
			 $("#new_category_button").html('Add');
			 $("#new_category_button").val('Add');
			 $("#new_category_section").show("normal");			
			 $("#new_category").focus();  
		} else if (this.value == 'del') {
			 $("#new_category_button").html('Delete');
			 $("#new_category_button").val('Del');
			 $("#new_category_section").show("normal");			
			 $("#new_category").focus();  			
		} else $("#new_category_section").hide("normal");;
	});
	
	$("#new_category_button").click(function(){		
		catVal = $("#new_category").val()
		action = $("#new_category_button").val()
		$('#new_category_section').hide("normal");
		$.get("change_category?action="+action+"&name="+catVal);
		if(action == 'Add') {
			$("#category").removeOption(catVal); /* avoid duplicates */
			$("#category").addOption(catVal, catVal, true);
			$("#category").removeOption('add'); /* move to the end */
			$("#category").addOption('add', '(add new)', false);
			$("#category").removeOption('del'); /* move to the end */
			$("#category").addOption('del', '(del existing)', false);					
		} else {
			$("#category").removeOption(catVal);
			$("#category").selectOptions('0', true);
		}
		return false;
	});

});

