<%!
from confapp.models import (
	DayType,
	HandoutType,
	SessionType,
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
	<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.11.2/css/all.min.css" integrity="sha256-+N4/V/SbAFiW1MPBCXnfnP9QSN3+Keu+NlB+0ev/YKQ=" crossorigin="anonymous" />
	<!-- Bootstrap -->
	<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
	<!-- ConfApp css -->
	<link href="/files/css/confapp.css" rel="stylesheet" />
	<!-- More bootstrap, etc -->
	<script src="https://code.jquery.com/jquery-3.6.1.min.js" integrity="sha256-o88AwQnZB+VDvE9tvIXrMQaPlFFSUTR+nldQm1LuPXQ=" crossorigin="anonymous"></script>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
	<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
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
	<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
		<button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarTogglerDemo01" aria-controls="navbarTogglerDemo01" aria-expanded="false" aria-label="Toggle navigation">
    	<span class="navbar-toggler-icon"></span>
  	</button>
		<a class="navbar-brand" href="${request.route_url("admin_home")}">Presenter DB</a>
		<div class="collapse navbar-collapse" id="navbarTogglerDemo01">
				<ul class="navbar-nav mr-auto">
% for type in DayType:
					<li class="nav-item ${"active" if section == type else ""}">
						<a class="nav-link" href="${request.route_url("admin_day_list", day=type.name)}">${type.name}</a>
					</li>
% endfor
% for thing in ("person", "session", "room"):
					<li class="nav-item ${"active" if request.matched_route.name.startswith("admin_%s_") else ""}">
						<a class="nav-link" href="${request.route_url("admin_%s_list" % thing)}">${thing.capitalize()}</a>
					</li>
% endfor
				</ul>
				<ul class="navbar-nav">
% if UserRole.SuperAdmin in request.effective_principals:
					<li class="nav-item ${"active" if request.matched_route.name.startswith("admin_user_") else ""}">
						<a class="nav-link" href="${request.route_url("admin_user_list")}">Users</a>
					</li>
					<li class="nav-item ${"active" if request.matched_route.name.startswith == "admin_admin" else ""}">
						<a class="nav-link" href="${request.route_url("admin_admin")}">Admin</a>
					</li>
% endif
% if request.authenticated_userid:
					<li class="nav-item"><span class="navbar-text">${request.authenticated_userid}</span></li>
					<li class="nav-item"><span><a href="${request.route_url("logout")}" class="btn btn-outline-info my-2 my-sm-0" role="button">Logout</a></span></li>
% else:
					<li class="nav-item"><span><a href="${request.route_url("login")}" class="btn btn-outline-info my-2 my-sm-0" role="button">Log in</a></span></li>
% endif
				</ul>
			</div> <!-- Other items collapsable -->
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
        <p class="text-muted">Some icons provided by <a href="https://fontawesome.com/">Fontawesome</a></p>
	</div>
</footer>
</body>
</html>
