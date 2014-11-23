<%!
from confapp.models import (
	DayType,
	HandoutType,
	PersonType,
	)
%>
<%def name="selectclslist(name, attr, cls, _class=None, _id=None)">
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
</%def>
<%def name="selectidlist(name, items, attr, default='')">
<select name="${name}">\
<option value="" selected="selected">(${default})</option>\
% for item in items:
<option value="${item.id}">${getattr(item, attr)}</option>\
% endfor
</select>\
</%def>
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html 
	PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head> 
	<meta http-equiv="content-type" content="text/html; charset=utf-8" />
	<title>Registration - ${section}</title>
	<style type="text/css" media="all">
		/* Thanks John Koh */
		html {
			margin: 0;
			padding: 0;
			height: 100%;
		}
		body {
			color: #000;
			font-family: Georgia, "Times New Roman", Times, serif;
			font-size: 11px;
			line-height: 11px;
			margin: 0;
			min-height: 100%;
		}
		#wrapper {
			width: auto;
			margin: 0;
			padding: 0;
			list-style-type: none;
		}
		#header {
			height: 4em;
			line-height: 4em;
		}
		#menu {
			background: rgb(195,228,247);/*#f3f3f3;*/
			border-top: 1px #000 solid;
			border-bottom: 1px #000 solid;
		}
		#menu_items {
			display: table;
			font-size: 18px;
			height: 36px;
			margin: 0;
			padding-left: 4em;
			text-align: center;
		}
		#HOME, #THURSDAY, #FRIDAY, #PERSON, #SESSION {
			display: table-cell;
			font-weight: bold;
			line-height: 47px;
			text-align: center;
			vertical-align: middle;
		}
		#HOME a, #THURSDAY a, #FRIDAY a, #PERSON a, #SESSION a {
			padding: 10px 0.75em 10px 0.75em;
			margin: auto 0.5em auto 0.5em;
		}
		#mainbody ol li {
			margin-top: 4px;
			margin-left: 0px;
			margin-bottom: 4px;
			list-style: none;
		}
		ol.mainbody {
			margin-top: 4px;
			margin-left: 0px;
			padding-left: 0px;
			margin-bottom: 4px;
			list-style: none;
		}
		li.header {
			margin-left: 40px;
			padding-left: 40px;
		}
		
		
		td.userodd { background-color:#DCD9FF;}
		td.usereven { background-color:#F3F2FF;}
		td.userselect { background-color:#FEF2FF;}
		
		td.sessionodd { background-color:#DCD9FF;}
		td.sessioneven { background-color:#F3F2FF;}
		td.sessionselect { background-color:#FEF2FF;}
		
		td.markercolor { background-color: #FFF5BF;}
		
		td.spacer { padding:0; background-color:#888888; }
		
		a.linkcell { height:100%;display:block; padding:0;}
		
		.table-cell-reg { display: table-cell; padding:0; color:#1F995C; text-align:center; }

		.table td.table-cell-bad-even { background-color:#FFD4E9; }
		.table td.table-cell-bad-odd { background-color:#FFE4F9; }
		.table td.code { width: 4em; }
		
		.table-header { font-weight:bold; padding:0.1em 0.1em 0.1em 0.1em; }
		th { padding:0.1em 0.1em 0.1em 0.1em; }
		
		.table { display: table; margin-left: 0em; padding-left: 0px; }
		a:link {color:#0066FF;}      /* unvisited link */
		a:visited {color:#0066FF;}  /* visited link */
		a:hover {color:#4DAFFF;}  /* mouse over link */
		a:active {color:#135C1D;}  /* selected link */
	</style>
	
	<!-- Bootstrap -->
	<link href="/files/css/bootstrap.min.css" rel="stylesheet" media="all" />

	<script type="text/javascript" src="/files/js/jquery-2.0.0.min.js"></script>
	<!-- Include all compiled plugins (below), or include individual files as needed -->
	<script type="text/javascript" src="/files/js/bootstrap.min.js"></script>
	
	<style media="all">
@media print {
	a[href]:after {
		content:none;
	}
	.table td.code { width: 10em; }
}
	</style>
	
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
</head> 
<body> 
${next.body()}
</body>
</html>