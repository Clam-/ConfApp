<%inherit file="admin-base.mako"/>
<div class="maxbig container-fluid">
<div class="col-sm-10">
<% day = section.description %>
	<h3>Registrations for ${day}</h3>

	<form class="form-inline" action="${request.route_url("admin_day_list", day=day)}" method="post">
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
				<th class="code"> Code </th>
				<th> Session title </th>
				<th> Room </th>
				<th colspan="2"> Eq O/I </th>
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
		
		session_id = session.id
		person_id = person.id
		
		if marker == "%s-%s" % (session_id, person_id):
			sessionstyle = "marker markercolor"
		else:
			sessionstyle = "session sessioneven" if count % 2 == 0 else "session sessionodd"
		
		if session.equipment == session.equip_returned:
			cellstyle = sessionstyle
		else:
			cellstyle = "table-cell-bad-even" if count % 2 == 0 else "table-cell-bad-odd"
		
		
		if name and code:
			uurl = request.route_url("admin_day_edit_nc", day=day, session=session_id, person=person_id, name=name, code=code)
		elif name:
			uurl = request.route_url("admin_day_edit_n", day=day, session=session_id, person=person_id, name=name)
		elif code:
			uurl = request.route_url("admin_day_edit_c", day=day, session=session_id, person=person_id, code=code)
		else:
			uurl = request.route_url("admin_day_edit", day=day, session=session_id, person=person_id)
		comments = session.comments
		loc = session.location
		other = session.other
		title = session.title
		bld, loc = loc.split(".", 1)
	%>
		<tr>
			<td class="table-cell-reg ${sessionstyle}">${u"\u2714" if item.registered else ""}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${person.lastname}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${person.firstname}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${item.type}</a></td>

			<td class="${sessionstyle} code"><a href="${uurl}" class="linkcell">${session.code}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${title[:24]+u"\u2026" if len(title) > 24 else title}</a></td>
% if len(loc) < 16:
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell"><strong>${bld}.</strong>${loc}</a></td>
% else:
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell"><abbr title="${loc}"><strong>${bld}.</strong>${loc[:15]+u"\u2026"}</abbr></a></td>
% endif
			<td class="${cellstyle}"><a href="${uurl}" class="linkcell">${session.equipment}</a></td>
			<td class="${cellstyle}"><a href="${uurl}" class="linkcell">${session.equip_returned}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${session.handouts}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${session.evaluations}</a></td>
% if other:
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell"><abbr title="${other}">${other[:5]}</abbr></a></td>
% else:
					<td class="${sessionstyle}"><a href="${uurl}" class="linkcell"></a></td>
% endif
% if comments:
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell"><abbr title="${comments}">${comments[:5]}</abbr></a></td>
% else:
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell"></a></td>
% endif
		</tr>
	<%	count += 1 %>
% endfor
	</table>
	<p>Page: ${page.pager()}</p>
</div>
<div id="sidebar" class="col-xs-2">
	<h3><a href="${request.route_url("admin_helper_list")}">Helpers</a> <a href="#" >&#8635;</a></h3>
	<table class="table">
	</table>
</div>
</div>