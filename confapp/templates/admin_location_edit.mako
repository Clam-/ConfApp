<%inherit file="admin-base.mako"/>
<div class="container">
	<div class="header">
		<h2><span>${"Editing" if item.id else "New"} Location</span>
% if item.id and admin:
		<a href="${request.route_url("admin_del", type=item.__tablename__, id=item.id)}" class="btn btn-danger float-right" role="button">Delete ${type(item).__name__}</a>
% endif
		</h2>
	</div>
	<form class="form" action="${request.route_url("admin_%s_edit" % item.__tablename__, id=item.id) if item.id else request.route_url("admin_%s_new" % item.__tablename__)}" method="post">
		<div class="form-group row">
			<label for="formId">ID</label>
			<input class="form-control" type="text" name="id" value="${item.id}" id="formId" readonly="readonly" >
		</div>
		<div class="form-group row">
			<label for="formBuildingNo">Building No.</label>
			<input class="form-control" type="text" name="buildingNo" value="${item.building.number if item.building else ""}" id="formBuildingNo" >
			<input type="hidden" name="buildingNo_orig" value="${item.building.number if item.building else ""}">
			<label for="formBuildingName">Building Name</label>
			<input class="form-control" type="text" name="buildingName" value="${item.building.name if item.building else ""}" id="formBuildingName" >
			<input type="hidden" name="buildingName_orig" value="${item.building.name if item.building else ""}">
			<label for="formBuildingAddr">Building Address</label>
			<input class="form-control" type="text" name="buildingAddr" value="${item.building.address if item.building else ""}" id="formBuildingAddr" >
			<input type="hidden" name="buildingAddr_orig" value="${item.building.address if item.building else ""}">
		</div>
		<div class="form-group row">
			<label for="formRoomNo">Room No.</label>
			<input class="form-control" type="text" name="room" value="${item.room}" id="formRoomNo">
			<input type="hidden" name="room_orig" value="${item.room}">
			<label for="formRoomName">Room Name</label>
			<input class="form-control" type="text" name="name" value="${item.name}" id="formRoomName">
			<input type="hidden" name="name_orig" value="${item.name}">
		</div>

		<button class="btn btn-primary" type="submit" name="form.submitted">Save</button>

		<div class="row">
			<div class="col-sm-2"></div>
			<div class="col-sm-8 assoc-list">
				<div class="pad-top"><p><span class="h4">Sessions</span></p></div>
				<table class="table table-sm">
					<thead class="thead-light">
						<tr>
							<th><i class="far fa-trash-alt"></i></th>
							<th>Type</th>
							<th>Code</th>
							<th>Session name</th>
						</tr>
					</thead>
					<tbody>
<% count = 0 %>
% for session in item.sessions:
<%
rowstyle = "row-even" if (count % 2 == 0) else "row-odd"

uurl = request.route_url("admin_session_edit", id=session.id)
%>
						<tr class="${rowstyle}">
							<td><input type="checkbox" name="removesess" value="${session.id}" ></td>
							<td><a href="${uurl}" class="linkcell">${session.sessiontype.name}</a></td>
							<td><a href="${uurl}" class="linkcell">${session.code}</a></td>
							<td><a href="${uurl}" class="linkcell">${session.title}</a></td>
						</tr>
<% count += 1 %>\
% endfor
					</tbody>
				</table>
			</div>
			<div class="col-sm-2"></div>
		</div>

		<input type="hidden" name="came_from" value="${came_from}">
		<button class="btn btn-primary" type="submit" name="form.submitted">Save</button>
	</form>
</li>
