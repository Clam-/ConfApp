<%inherit file="admin-base.mako"/>
<div class="maxbig">
	<h2>Registrations for ${section.description}</h2>

	<form class="form-inline" action="${request.route_url("admin_day_list", day=section.description)}" method="post">
		<div class="form-group">
			<label class="sr-only control-label" for="formName">Search name:</label>
			<input class="form-control" id="formName" type="text" name="search.name" value="${name}" placeholder="Name"/>
		</div>
		<div class="form-group">
			<label class="sr-only control-label" for="formCode">Code:</label>
			<input class="form-control" id="formCode" type="text" name="search.code" value="${code}" placeholder="Code"/>
		</div>
		<button type="submit" class="btn btn-default" name="form.submitted">Search</button>
	</form>
	<table class="table">
		<thead class="table-header">
			<tr>
				<th> Reg&rsquo;d </th>
				<th> Last name </th>
				<th> First name </th>
				<th> Type </th>
				<th class="spacer"></th>
				<th> Code </th>
				<th> Session title </th>
				<th> Room </th>
				<th> Eq Out </th>
				<th> Eq In </th>
				<th> Handouts </th>
				<th> Evaluations </th>
				<th> Other </th>
				<th> Comment </th>
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
		if marker == "%s-%s" % (session.id, person.id):
			sessionstyle = "marker markercolor"
		else:
			sessionstyle = "session sessioneven" if count % 2 == 0 else "session sessionodd"
		
		if session.equipment == session.equip_returned:
			cellstyle = sessionstyle
		else:
			cellstyle = "table-cell-bad-even" if count % 2 == 0 else "table-cell-bad-odd"
		
		if name and code:
			uurl = request.route_url("admin_day_edit_nc", day=section.description, session=session.id, person=person.id, name=name, code=code)
		elif name:
			uurl = request.route_url("admin_day_edit_n", day=section.description, session=session.id, person=person.id, name=name)
		elif code:
			uurl = request.route_url("admin_day_edit_c", day=section.description, session=session.id, person=person.id, code=code)
		else:
			uurl = request.route_url("admin_day_edit", day=section.description, session=session.id, person=person.id)
	%>
		<tr>
			<td class="table-cell-reg ${sessionstyle}">${u"\u2714" if item.registered else ""}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${person.lastname}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${person.firstname}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${item.type}</a></td>
			
			<td class="spacer"></td>
			
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${session.code}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${session.title[:25]}&hellip;</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${session.location if len(session.location) < 20 else session.location[:20]+ u"\u2026"}</a></td>
			<td class="${cellstyle}"><a href="${uurl}" class="linkcell">${session.equipment}</a></td>
			<td class="${cellstyle}"><a href="${uurl}" class="linkcell">${session.equip_returned}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${session.handouts}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${session.evaluations}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${session.other}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${session.comments}</a></td>
		</tr>
	<%	count += 1 %>
% endfor
	</table>
	<p>Page: ${page.pager()}</p>
</div>