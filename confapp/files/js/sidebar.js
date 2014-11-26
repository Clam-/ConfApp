var timeoutLooper = null;
function get_updates () {
	if (timeoutLooper != null) {
		clearTimeout(timeoutLooper)
	}
	$('#sidebar table').load("/helperupdate/");
	timeoutLooper = setTimeout(get_updates, 15000);
}

$( document ).ready( 
function() {
    $('#sidebar a').click(function () {
		get_updates();
    });
    get_updates();

});
function helper_returned(url) {
	$('#sidebar table').load(url);
	//timeoutLooper = setTimeout(get_updates, 15000);
}
	