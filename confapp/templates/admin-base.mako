<%!
from confapp.models import (
	DayType,
	HandoutType,
	PersonType,
	UserRole,
	)
from confapp.security import (
	checkAdmin,
	checkSport,
	checkMain,
	)
%>\
<%def name="selectclslist(name, attr, cls, _class=None, _id=None)">\
% if _class:
<select class="${_class}" name="${name}" id="${_id}">\
% else:
<select name="${name}">\
% endif
% for item in cls:
%	if attr == cls(item.value):
<option value="${item.value}" selected="selected">${item.name}</option>\
% 	else:
<option value="${item.value}">${item.name}</option>\
%	endif
% endfor
</select>\
</%def>\
<%def name="selectidlist(name, items, attrs, default='', value='', _class=None, _id=None)">\
% if _class:
<select class="${_class}" name="${name}" id="${_id}">\
% else:
<select name="${name}">\
% endif
<option value="" ${"" if value else 'selected="selected"'}>(${default})</option>\
% for item in items:
<option value="${item.id}" ${'selected="selected"' if value == item.id else ""} >${getattr(item, attrs[0])}.${getattr(item, attrs[1])}</option>\
% endfor
</select>\
</%def>\
<%
mainen = checkMain(request.effective_principals)
sporten = checkSport(request.effective_principals)
admin = checkAdmin(request.effective_principals)
%>\
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
	$('.utcdate').text(function(i,oldtext){
		return new Date( oldtext.concat("Z") ).toLocaleString();
	});
});
</script>
</head>
<body>
	<nav class="navbar navbar-default">
		<div class="container-fluid">
			<!-- group main collapsable button and title together for better display -->
			<div class="navbar-header">
				<button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
					<span class="sr-only">Toggle navigation</span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
			  </button>
			  <a class="navbar-brand" href="${request.route_url("admin_home")}">Presenter DB</a>
			</div>

			<!-- Collapsable other items -->
			<div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
				<ul class="nav navbar-nav">
% for type in DayType:
					<li class="${"active" if section == type else ""}">
						<a href="${request.route_url("admin_day_list", day=type.name)}">${type.name}</a>
					</li>
% endfor
% for thing in ("person", "session", "room"):
					<li class="${"active" if request.matched_route.name.startswith("admin_%s_") else ""}">
						<a href="${request.route_url("admin_%s_list" % thing)}">${thing.capitalize()}</a>
					</li>
% endfor
				</ul>
				<ul class="nav navbar-nav navbar-right">
% if UserRole.SuperAdmin in request.effective_principals:
					<li class="${"active" if request.matched_route.name.startswith("admin_user_") else ""}">
						<a href="${request.route_url("admin_user_list")}">Users</a>
					</li>
					<li class="nav-item ${"active" if request.matched_route.name.startswith == "admin_admin" else ""}">
						<a class="nav-link" href="${request.route_url("admin_admin")}">Admin</a>
					</li>
% endif
% if request.authenticated_userid:
					<li><p class="navbar-text">${request.authenticated_userid}</p></li>
					<li ><span><a href="${request.route_url("logout")}" class="btn btn-info navbar-btn" role="button">Logout</a></span></li>
% else:
					<li ><span><a href="${request.route_url("login")}" class="btn btn-info navbar-btn" role="button">Log in</a></span></li>
% endif
				</ul>
			</div> <!-- Other items collapsable -->
		</div>
	</nav>

<% msgs = request.session.pop_flash() %>
% if msgs:
<div class="container">
	<ul class="list-unstyled bg-danger">
	% for msg in msgs:
		<li> ${msg} </li>
	% endfor
	</ul>
</div>
% endif
${next.body(mainen=mainen, sporten=sporten, admin=admin)}
<footer class="footer">
	<div class="container">
        <p class="text-muted pad-top">Some icons provided by <a href="http://glyphicons.com/">GLYPHICONS</a></p>
	</div>
</footer>
</body>
</html>
