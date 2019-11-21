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
<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">

	<title>Registration - ${section}</title>
	<!-- Bootstrap -->
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css"
		integrity="sha512-dTfge/zgoMYpP7QbHy4gWMEGsbsdZeCXz7irItjcC3sPUFtf0kuFbDz/ixG7ArTxmDjLXDmezHubeNikyKGVyQ==" crossorigin="anonymous" />
	<!-- ConfApp css -->
	<link href="/files/css/confapp.css" rel="stylesheet" />
	<!-- More bootstrap, etc -->
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
	<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"
		integrity="sha512-K1qjQ+NcF2TYO/eI3M6v8EiNYZfA95pQumfvcVrTHtwQVDG+aHRqLi/ETn2uB+1JqwYqVG3LIvdm9lj6imS/pQ==" crossorigin="anonymous">
	</script>
	<script type="text/javascript">
$( document ).ready(
function() {
	$("tbody>tr").hover(
		function() {
			$( this ).toggleClass( "row-hover" );
		}, function() {
			$( this ).toggleClass( "row-hover" );
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
