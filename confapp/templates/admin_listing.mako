<%inherit file="admin-base.mako"/>
<script type="text/javascript" src="/files/js/sidebar.js"></script>
<div class="container-fluid">
% if logged_in == "main" and helpers:
<div class="col-sm-10">
% endif
<% day = section.name %>
	<div class="header">
		<h3>Registrations for ${day}</h3>
	</div>
	<form class="form-inline" action="${request.route_url("admin_day_list", day=day)}" method="post">
		<div class="form-group">
			<label class="sr-only control-label" for="formName">Search name</label>
			<input class="form-control" id="formName" type="text" name="search.name" value="${name}" placeholder="Name" autofocus />
		</div>
		<div class="form-group">
			<label class="sr-only control-label" for="formCode">Code</label>
			<input class="form-control" id="formCode" type="text" name="search.code" value="${code}" placeholder="Code"/>
		</div>
		<button type="submit" class="btn btn-default" name="form.submitted">Search</button>
	</form>
	<table class="table table-condensed">
		<thead class="table-header">
			<tr>
				<th><abbr title="Main check-in">Mn</abbr></th>
				<th><abbr title="Sports Centre check-in">Sp</abbr></th>
				<th>Last name</th>
				<th>First name</th>
				<th>Type</th>
<%
		if name and code:
			uurl = request.route_url("admin_day_search", day=day, name=name, code=code, _query={"sort":"code"})
		elif name:
			uurl = request.route_url("admin_day_search_n", day=day,  name=name, _query={"sort":"code"})
		elif code:
			uurl = request.route_url("admin_day_search_c", day=day,  code=code, _query={"sort":"code"})
		else:
			uurl = request.route_url("admin_day_list", day=day, _query={"sort":"code"})
%>
				<th class="code"><a href="${uurl}">Code</a></th>
				<th>Session title</th>
				<th><abbr title="Building">Bld</abbr>.Room</th>
				<th colspan="2"><abbr title="Equipment Out/In">Eq O/I</abbr></th>
				<th>Handouts</th>
				<th><abbr title="Evaluation forms">Evals</abbr></th>
				<th>Other</th>
				<th>Comment</th>
			</tr>
		</thead>
<%
count = 0
items = page.items
sport = False
%>
% for item in items:
	<%
		session = item.session
		person = item.person

		session_id = session.id
		person_id = person.id

		if session.room and (session.room.building.number == "1") or session.room.building.number == "23": sport = True # or session.room.building.number == "60"
		else: sport = False

		if marker == "%s-%s" % (session_id, person_id):
			rowstyle = "row-marker"
		else:
			rowstyle = "row-even" if count % 2 == 0 else "row-odd"

		if session.equipment == session.equip_returned:
			equipstyle = ""
		else:
			equipstyle = "table-cell-bad-even" if count % 2 == 0 else "table-cell-bad-odd"


		if name and code:
			uurl = request.route_url("admin_day_edit_nc", day=day, session=session_id, person=person_id, name=name, code=code)
		elif name:
			uurl = request.route_url("admin_day_edit_n", day=day, session=session_id, person=person_id, name=name)
		elif code:
			uurl = request.route_url("admin_day_edit_c", day=day, session=session_id, person=person_id, code=code)
		else:
			uurl = request.route_url("admin_day_edit", day=day, session=session_id, person=person_id)
		comments = session.comments
		room = session.room
		other = session.other
		title = session.title

		if sport:
			sporttick = u"\u2714" if item.registered_sport else u"\u2717"
		else:
			sporttick = "-"
	%>
		<tr class="${rowstyle}">
			<td><a href="${uurl}" class="linkcell ${"text-success" if item.registered else "text-muted"}">${u"\u2714" if item.registered else u"\u2717"}</a></td>
% if sport:
			<td><a href="${uurl}" class="linkcell ${"text-success" if item.registered_sport else "text-muted"}">${sporttick}</a></td>
% else:
			<td><a href="${uurl}" class="linkcell text-muted"></a></td>
% endif
			<td><a href="${uurl}" class="linkcell">${person.lastname}</a></td>
			<td><a href="${uurl}" class="linkcell">${person.firstname}</a></td>
			<td><a href="${uurl}" class="linkcell">${item.type}</a></td>

			<td class="code"><a href="${uurl}" class="linkcell">${session.code}</a></td>
			<td><a href="${uurl}" class="linkcell">${title[:24]+u"\u2026" if len(title) > 24 else title}</a></td>
% if room:
			<td><a href="${uurl}" class="linkcell"><strong>${room.building.number}.</strong>${room.name}</a></td>
% else:
			<td><a href="${uurl}" class="linkcell"><strong>Oops.</strong><abbr title=""></abbr></a></td>
% endif
			<td class="${equipstyle}"><a href="${uurl}" class="linkcell">${session.equipment}</a></td>
			<td class="${equipstyle}"><a href="${uurl}" class="linkcell">${session.equip_returned}</a></td>
			<td><a href="${uurl}" class="linkcell">${session.handouts}</a></td>
			<td><a href="${uurl}" class="linkcell">${session.evaluations}</a></td>
% if other and len(other) > 5:
			<td><a href="${uurl}" class="linkcell"><abbr title="${other}">${other[:5]}</abbr></a></td>
% else:
			<td><a href="${uurl}" class="linkcell">${other}</a></td>
% endif
% if comments:
			<td><a href="${uurl}" class="linkcell"><abbr title="${comments}">${comments[:5]}</abbr></a></td>
% else:
			<td><a href="${uurl}" class="linkcell"></a></td>
% endif
		</tr>
	<%	count += 1 %>
% endfor
	</table>
	<p>Page: ${page.pager()}</p>
</div>
% if logged_in == "main" and helpers:
<div id="sidebar" class="col-xs-2">
	<h3><a href="${request.route_url("admin_helper_list")}">Helpers</a> <a href="#" >&#8635;</a></h3>
	<table class="table">
	</table>
</div>
% endif
</div>
