<%inherit file="admin-base.mako"/>
<div class="container">
	<div class="header">
		<h2>${section.capitalize()} list</h2>
	</div>

	<form class="form-inline" action="${request.route_url("admin_person_list", day=section)}" method="post">
		<div class="form-group">
			<label class="sr-only control-label" for="formName">Search name</label>
			<input class="form-control" id="formName" type="text" name="search.name" value="" placeholder="Name" autofocus />
		</div>
		<div class="form-group">
			<label class="sr-only control-label" for="formCode">Code</label>
			<input class="form-control" id="formCode" type="text" name="search.code" value="" placeholder="Code"/>
		</div>
		<button type="submit" class="btn btn-default" name="form.submitted">Search</button>
		<a href="${request.route_url("admin_person_new")}" class="btn btn-info pull-right" role="button">New</a>
	</form>
	

	<table class="table">
		<thead class="table-header">
			<tr>
				<th> ID </th>
				<th> Last name </th>
				<th> First name </th>
				<th> Phone </th>
				<th> Email </th>
			</tr>
		</thead>
	<% count = 0 %>
% for item in page.items:
	<%	
		if marker == str(item.id):
			rowstyle = "row-marker"
		else:
			rowstyle = "row-even" if count % 2 == 0 else "row-odd"
		
		uurl = request.route_url("admin_person_edit", id=item.id)
	%>
		<tr class="${rowstyle}">
			<td><a href="${uurl}" class="linkcell">${item.id}</a></td>
			<td><a href="${uurl}" class="linkcell">${item.lastname}</a></td>
			<td><a href="${uurl}" class="linkcell">${item.firstname}</a></td>
			<td><a href="${uurl}" class="linkcell">${item.phone.replace("\n"," | ") if item.phone else ""}</a></td>
			<td><a href="${uurl}" class="linkcell">${item.email.replace("\n",";") if item.email else ""}</a></td>
			
		</tr>
	<%	count += 1 %>
% endfor
	</table>
	<p> Page: ${page.pager()} </p>

</div>