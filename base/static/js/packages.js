$(document).ready(function() {
	  
	$('button').click(function() {	
		var mySplitResult = this.id.split("_");
		var class_str = mySplitResult[0];
		var id_num =  mySplitResult[1];
		var css_display = 'none';
		/* first we set all class buttons to the unclicked status */
		$('#main_'+id_num).removeClass("down");
		$('#optional_'+id_num).removeClass("down");
		$('#internal_'+id_num).removeClass("down");		
		/* set the clicked button down */
		$(this).toggleClass("down");
		$row = $(this).parent().parent();				
		if (this.value == 'M') {
			css_display = 'table-row';
		};
		$('#linked_app_'+id_num).css('display', css_display);
		
		$.get("/packages/set_class/", { package_id: id_num, install_class: this.value } );
	});
});

/* autocomplete */
$(document).ready(function() {
	$("#SearchPackage").autocomplete(
		"search",
		{
			delay:10,
			minChars:2,
			matchSubset:1,
			matchContains:1,
			cacheLength:10,
			onItemSelect:selectItem,
			onFindValue:findValue,
			formatItem:formatItem,
			autoFill:true
		}
	);
});

function findValue(li) {
	if( li == null ) return alert("No match!");

	// if coming from an AJAX call, let's use the CityId as the value
	if( !!li.extra ) var sValue = li.extra[0];

	// otherwise, let's just display the value in the text box
	else var sValue = li.selectValue;
	
	window.location = "?q="+li.selectValue
	//alert("The value you selected was: " + sValue);
}

function selectItem(li) {
	findValue(li);
}

function formatItem(row) {
	return row[0] + " (id: " + row[1] + ")";
}

function lookupAjax(){
	var oSuggest = $("#SearchPackage")[0].autocompleter;

	oSuggest.findValue();

	return false;
}

