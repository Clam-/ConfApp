<%inherit file="admin-base.mako"/>
<div class="container">
	<h2>${section.capitalize()} list</h2>
	<a href="${request.route_url("admin_user_new")}" class="btn btn-info float-right" role="button">New</a>
	<table class="table table-condensed">
		<thead class="table-header">
			<tr>
				<th> ID </th>
				<th> Username </th>
				<th> Name </th>
				<th> Role </th>
				<th> Last seen </th>
			</tr>
		</thead>
	<% count = 0 %>
% for item in page.items:
	<%
		rowstyle = "row-even" if count % 2 == 0 else "row-odd"

		surl = request.route_url("admin_user_edit", id=item.id)
	%>
		<tr class="${rowstyle}">
			<td><a href="${surl}" class="linkcell">${item.id}</a></td>
			<td><a href="${surl}" class="linkcell">${item.username}</a></td>
			<td><a href="${surl}" class="linkcell">${item.name}</a></td>
			<td><a href="${surl}" class="linkcell">${item.role.name}</a></td>
			<td><a href="${surl}" class="linkcell"><span class="utcdate">${item.lastseen.isoformat() if item.lastseen else "" }</span></a></td>
		</tr>
	<%	count += 1 %>
% endfor
	</table>
	<p> Page: ${page.pager()} </p>
</div>
