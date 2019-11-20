<%inherit file="admin-base.mako"/>
<div class="container-fluid">
	<h2>${section.capitalize()} list</h2>

	<form class="form-inline" action="${request.route_url("admin_session_list", day=section)}" method="post">
		<div class="form-group">
			<label class="sr-only control-label" for="formName">Search title</label>
			<input class="form-control" id="formName" type="text" name="search.title" value="${title}" placeholder="Title" autofocus />
		</div>
		<div class="form-group">
			<label class="sr-only control-label" for="formCode">Code</label>
			<input class="form-control" id="formCode" type="text" name="search.code" value="${code}" placeholder="Code"/>
		</div>
		<button type="submit" class="btn btn-default" name="form.submitted">Search</button>
		<a href="${request.route_url("admin_session_new")}" class="btn btn-info pull-right" role="button">New</a>
	</form>
	<table class="table table-condensed">
		<thead class="table-header">
			<tr>
				<th> Code </th>
				<th> Session title </th>
				<th> Building.room </th>
				<th> Eq Out </th>
				<th> Eq In </th>
				<th> <a href="${request.route_url("admin_session_list", _query={"sort":"handouts"})}">Handouts</a> </th>
				<th> Evaluations </th>
				<th> Other </th>
				<th> Comment </th>
			</tr>
		</thead>
	<% count = 0 %>
% for item in page.items:
	<%
		if marker == str(item.id):
			rowstyle = "row-marker"
		else:
			rowstyle = "row-even" if count % 2 == 0 else "row-odd"

		if item.equipment == item.equip_returned:
			equipstyle = ""
		else:
			equipstyle = "table-cell-bad-even" if count % 2 == 0 else "table-cell-bad-odd"
		surl = request.route_url("admin_session_edit", id=item.id)
	%>
		<tr class="${rowstyle}">
			<td><a href="${surl}" class="linkcell">${item.code}</a></td>
			<td><a href="${surl}" class="linkcell">${"<s>" if item.cancelled else "" | n}${item.title}${"</s>" if item.cancelled else "" | n}</a></td>
% if item.room:
			<td><a href="${surl}" class="linkcell"><strong>${item.room.building.number}</strong>.${item.room.name}</a></td>
% else:
			<td><a href="${surl}" class="linkcell"><strong></strong>.</a></td>
% endif
			<td class="${equipstyle}"><a href="${surl}" class="linkcell">${item.equipment}</a></td>
			<td class="${equipstyle}"><a href="${surl}" class="linkcell">${item.equip_returned}</a></td>
			<td><a href="${surl}" class="linkcell">${item.handouts.name}</a></td>
			<td><a href="${surl}" class="linkcell">${item.evaluations.name}</a></td>
			<td><a href="${surl}" class="linkcell">${item.other}</a></td>
			<td><a href="${surl}" class="linkcell">${item.comments}</a></td>
		</tr>
	<%	count += 1 %>
% endfor
	</table>
	<p> Page: ${page.pager() | n } </p>
</div>
