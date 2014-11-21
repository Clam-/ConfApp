<%inherit file="admin-base.mako"/>
<div class="maxbig">
	<h2>${section.capitalize()} list</h2>

	<form class="form-inline" action="${request.route_url("admin_session_list", day=section)}" method="post">
		<div class="form-group">
			<label class="sr-only control-label" for="formName">Search title:</label>
			<input class="form-control" id="formName" type="text" name="search.title" value="${title}" placeholder="Title"/>
		</div>
		<div class="form-group">
			<label class="sr-only control-label" for="formCode">Code:</label>
			<input class="form-control" id="formCode" type="text" name="search.code" value="${code}" placeholder="Code"/>
		</div>
		<button type="submit" class="btn btn-default" name="form.submitted">Search</button>
	</form>
	<table class="table table-condensed">
		<thead class="table-header">
			<tr>
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
	<% count = 0 %>
% for item in page.items:
	<%	
		if marker == str(item.id):
			userstyle = "marker markercolor"
			sessionstyle = "marker markercolor"
		else:
			sessionstyle = "session sessioneven" if count % 2 == 0 else "session sessionodd"
		
		if item.equipment == item.equip_returned:
			cellstyle = sessionstyle
		else:
			cellstyle = "table-cell-bad-even" if count % 2 == 0 else "table-cell-bad-odd"
		surl = request.route_url("admin_session_edit", id=item.id)
	%>
		<tr>
			<td class="code ${sessionstyle}"><a href="${surl}" class="linkcell">${item.code}</a></td>
			<td class="${sessionstyle}"><a href="${surl}" class="linkcell">${item.title}</a></td>
			<td class="${sessionstyle}"><a href="${surl}" class="linkcell">${item.location}</a></td>
			<td class="${cellstyle}"><a href="${surl}" class="linkcell">${item.equipment}</a></td>
			<td class="${cellstyle}"><a href="${surl}" class="linkcell">${item.equip_returned}</a></td>
			<td class="${sessionstyle}"><a href="${surl}" class="linkcell">${item.handouts}</a></td>
			<td class="${sessionstyle}"><a href="${surl}" class="linkcell">${item.evaluations}</a></td>
			<td class="${sessionstyle}"><a href="${surl}" class="linkcell">${item.other}</a></td>
			<td class="${sessionstyle}"><a href="${surl}" class="linkcell">${item.comments}</a></td>
		</tr>
	<%	count += 1 %>
% endfor
	</table>
	<p> Page: ${page.pager()} </p>
</div>