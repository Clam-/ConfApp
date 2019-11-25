<%inherit file="admin-base.mako"/>
<div class="container">
	<h2>${section.capitalize()} list</h2>
	<a href="${request.route_url("admin_room_new")}" class="btn btn-info float-right" role="button">New</a>
	<table class="table table-sm">
		<thead class="thead-light">
			<tr>
				<th> ID </th>
				<th> Building </th>
				<th> Room </th>
				<th> Sessions </th>
			</tr>
		</thead>
	<% count = 0 %>
% for item in page.items:
	<%
		rowstyle = "row-even" if count % 2 == 0 else "row-odd"

		surl = request.route_url("admin_room_edit", id=item.id)
	%>
		<tr class="${rowstyle}">
			<td><a href="${surl}" class="linkcell">${item.id}</a></td>
% if item.building:
			<td><a href="${surl}" class="linkcell">${item.building.number}</a></td>
% else:
			<td><a href="${surl}" class="linkcell">-</a></td>
% endif
			<td><a href="${surl}" class="linkcell">${item.room} (${item.name})</a></td>
			<td><a href="${surl}" class="linkcell">${len(item.sessions)}</a></td>
		</tr>
	<%	count += 1 %>
% endfor
	</table>
	<p> Page: ${page.pager()} </p>
</div>
