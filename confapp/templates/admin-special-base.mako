<%!
from confapp.models import (
	DayType,
	HandoutType,
	PersonType,
	)
%>\
<%def name="selectclslist(name, attr, cls, _class=None, _id=None)">\
% if _class:
<select class="${_class}" name="${name}" id="${_id}">\
% else:
<select name="${name}">\
% endif
% for key, description in cls:
%	if attr == cls.from_string(key):
<option value="${key}" selected="selected">${description}</option>\
% 	else:
<option value="${key}">${description}</option>\
%	endif
% endfor
</select>\
</%def>\
<%def name="selectidlist(name, items, attrs, default='', _class=None, _id=None)">\
% if _class:
<select class="${_class}" name="${name}" id="${_id}">\
% else:
<select name="${name}">\
% endif
<option value="" selected="selected">(${default})</option>\
% for item in items:
<option value="${item.id}">${getattr(item, attrs[0])}.${getattr(item, attrs[1])[:1]}</option>\
% endfor
</select>\
</%def>\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html 
	PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head> 
	<meta http-equiv="content-type" content="text/html; charset=utf-8" />
	<title>Registration - ${section}</title>
	<link href="/files/css/confapp-special.css" rel="stylesheet" />
	<!-- Bootstrap -->
	<link href="/files/css/bootstrap.min.css" rel="stylesheet" />
	<!-- Override -->
	<style type="text/css">
		.table>thead>tr>th {padding:0.3em 0.3em 0.3em 0.3em;}
		.table>tbody>tr>td {padding:0.3em 0.3em 0.3em 0.3em;}
	</style>
	<script type="text/javascript" src="/files/js/jquery-2.1.1.min.js"></script>
	<!-- Include all compiled plugins (below), or include individual files as needed -->
	<script type="text/javascript" src="/files/js/bootstrap.min.js"></script>
	<script type="text/javascript">
$( document ).ready( 
function() {
	$("td.user").hover(
		function() {
			$( this ).parent().children("td.user").toggleClass( "userselect" );
			$( this ).parent().children("td.user").toggleClass( "userodd" );
		}, function() {
			$( this ).parent().children("td.user").toggleClass( "userodd" );
			$( this ).parent().children("td.user").toggleClass( "userselect" );
		}
	);
	$("td.session").hover(
		function() {
			$( this ).parent().children("td.session").toggleClass( "sessionselect" );
			$( this ).parent().children("td.session").toggleClass( "sessionodd" );
		}, function() {
			$( this ).parent().children("td.session").toggleClass( "sessionodd" );
			$( this ).parent().children("td.session").toggleClass( "sessionselect" );
		}
	);
	$("td.marker").hover(
		function() {
			$( this ).parent().children("td.marker").toggleClass( "userselect" );
			$( this ).parent().children("td.marker").toggleClass( "markercolor" );
		}, function() {
			$( this ).parent().children("td.marker").toggleClass( "markercolor" );
			$( this ).parent().children("td.marker").toggleClass( "userselect" );
		}
	);
});
</script>
	<style media="all">
@media print {
	a[href]:after {
		content:none;
	}
	.table td.code { width: 10em; }
}
	</style>
</head>  
<body> 
${next.body()}
</body>
</html>