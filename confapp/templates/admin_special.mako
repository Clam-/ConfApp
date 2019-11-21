<%inherit file="admin-special-base.mako"/>
<div class="container-fluid">
<% day = section.name %>
	<h2>Registrations for ${section.name}</h2>
	<table class="table">
		<thead class="table-header">
			<tr>
				<th>Mn</th>
				<th>Sp</th>
				<th>Last name</th>
				<th>First name</th>
				<th>Type</th>
				<th class="code">Code</th>
				<th>Session title</th>
				<th>Evaluations</th>
				<th>Handouts</th>
				<th>Comment</th>
			</tr>
		</thead>
<%
count = 0
items = page.items
%>

% for item in items:
	<%
		session = item.session
		person = item.person

		session_id = session.id
		person_id = person.id

		if session.building == "1": sport = True
		else: sport = False

		if marker == "%s-%s" % (session_id, person_id):
			rowstyle = "row-marker"
		else:
			rowstyle = "row-even" if count % 2 == 0 else "row-odd"

		if session.equipment == session.equip_returned:
			equipstyle = ""
		else:
			equipstyle = "table-cell-bad-even" if count % 2 == 0 else "table-cell-bad-odd"


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
			<td><a href="${uurl}" class="linkcell">${str(item.type.name)[:4]}</a></td>

			<td><a href="${uurl}" class="linkcell">${session.code}</a></td>
			<td><a href="${uurl}" class="linkcell">${title[:24]+u"\u2026" if len(title) > 24 else title}</a></td>
			<td><a href="${uurl}" class="linkcell">${session.evaluations.name}</a></td>
			<td><a href="${uurl}" class="linkcell">${session.handouts.name}</a></td>
			<td><a href="${uurl}" class="linkcell">${session.comments}</a></td>
		</tr>
	<%	count += 1 %>
% endfor
	</table>
</div>
