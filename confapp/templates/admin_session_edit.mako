<%inherit file="admin-base.mako"/>\
<%page args="mainen, sporten, admin"/>\
<div class="container">
	<div class="header">
		<h2><span>${"Editing" if item.id else "New"} Session ${"CANCELLED" if item.cancelled else ""}</span>
% if item.id and admin:
		<a href="${request.route_url("admin_del", type=item.__tablename__, id=item.id)}" class="btn btn-danger float-right" role="button">Delete ${type(item).__name__}</a>
% endif
		</h2>
	</div>
	<form action="${request.route_url("admin_session_edit", id=item.id) if item.id else request.route_url("admin_session_new")}" method="post">

		<div class="form-group row">
			<label class="col-sm-1 col-form-label" for="formCode">Code</label>
			<div class="col-sm-1">
				<input class="form-control" type="text" name="code" value="${item.code}" id="formCode" ${'readonly="readonly"' if not admin else ""}>
				<input type="hidden" name="code_orig" value="${item.code}">
			</div>
			<label class="col-sm-1 col-form-label" for="formDay">Day</label>
			<div class="col-sm-2">
				${self.selectclslist("day", item.day, self.attr.DayType, _class="form-control", _id="formDay")}
				<input type="hidden" name="day_orig" value="${item.day.value if item.day else ""}">
			</div>
			<label class="col-sm-2 col-form-label" for="formSessionTitle">Session title</label>
			<div class="col-sm-5">
				<input class="form-control" type="text" name="title" value="${item.title}" id="formSessionTitle" ${'readonly="readonly"' if not admin else ""}>
				<input type="hidden" name="title_orig" value="${item.title}">
			</div>
		</div>

		<div class="form-group row">
			<label class="col-sm-1 col-form-label" for="formBuilding">Building No.</label>
			<div class="col-sm-1">
				<input class="form-control" type="text" name="building" value="${item.room.building.number if item.room else ""}" id="formBuilding" readonly >
				<input type="hidden" name="building_orig" value="${item.room.building.number if item.room else ""}">
			</div>
			<label class="col-sm-1 col-form-label" for="formRoom">Room</label>
			<div class="col-sm-4">
% if admin:
				${self.selectidlist("room", rooms, ("building", "name"), "Select Room", item.room.id, _class="form-control", _id="formRoom")}
% else:
				<input class="form-control" type="text" name="room" value="${item.room.name if item.room else ""}" id="formRoom" readonly>
% endif
				<input type="hidden" name="room_orig" value="${item.room.id if item.room else ""}">
			</div>
			<label class="col-sm-1 col-form-label" for="formSTime">Time</label>
			<div class="col-sm-2">
				<input class="form-control" type="text" name="time" value="${item.time}" id="formSTime" ${'readonly="readonly"' if not admin else ""}>
				<input type="hidden" name="time_orig" value="${item.time}">
			</div>
		</div>

		<div class="form-group row">
			<label class="col-sm-2 col-form-label" for="formHandouts">Handouts (Said: ${item.handouts_said.name})</label>
			<div class="col-sm-3">
				${self.selectclslist("handouts", item.handouts, self.attr.HandoutType, _class="form-control", _id="formHandouts")}
				<input type="hidden" name="handouts_orig" value="${item.handouts.value}">
			</div>
			<label class="col-sm-2 col-form-label" for="formEval">Evaluations (${item.evaluations.name})</label>
			<div class="col-sm-3">
				${self.selectclslist("evaluations", item.evaluations, self.attr.HandoutType, _class="form-control", _id="formEval")}
				<input type="hidden" name="evaluations_orig" value="${item.evaluations.value}">
			</div>
		</div>

		<div class="form-group row">
			<label class="col-sm-2 col-form-label" for="formEquipmentBorrowed">Equipment borrowed</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="equipment" value="${item.equipment}" id="formEquipmentBorrowed">
				<input type="hidden" name="equipment_orig" value="${item.equipment}">
			</div>
			<label class="col-sm-2 col-form-label" for="formEquipmentReturned">Equipment returned</label>
			<div class="col-sm-5">
				<input class="form-control" type="text" name="equip_returned" value="${item.equip_returned}" id="formEquipmentReturned">
				<input type="hidden" name="equip_returned_orig" value="${item.equip_returned}">
			</div>
		</div>

		<div class="form-group row">
			<label class="col-sm-2 col-form-label" for="formComment">Comment</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="comments" value="${item.comments}" id="formComment">
				<input type="hidden" name="comments_orig" value="${item.comments}">
			</div>
			<label class="col-sm-2 col-form-label" for="formOther">Other</label>
			<div class="col-sm-5">
				<input class="form-control" type="text" name="other" value="${item.other}" id="formOther">
				<input type="hidden" name="other_orig" value="${item.other}">
			</div>
		</div>

<%
facs = item.facilities_req
faclen = facs.count("\n")
if faclen < 2:
	faclen = 2
%>\
		<div class="form-group row">
			<label class="col-sm-2 col-form-label" for="formFacilitiesReq">Facilities Requested</label>
			<div class="col-sm-3">
				<textarea class="form-control" name="facilities_req" rows="${faclen}" cols="20" id="formFacilitiesReq">${facs}</textarea>
				<input type="hidden" name="facilities_req_orig" value="${item.facilities_req}">
			</div>
<%
facs = item.facilities_got
faclen = facs.count("\n")
if faclen < 2:
	faclen = 2
%>\
			<label class="col-sm-2 col-form-label" for="formFacilitiesGot">Facilities Available</label>
			<div class="col-sm-5">
				<textarea class="form-control" name="facilities_got" rows="${faclen}" cols="20" id="formFacilitiesGot">${facs}</textarea>
				<input type="hidden" name="facilities_got_orig" value="${item.facilities_got}">
			</div>
		</div>

		<div class="form-group row">
			<div class="col-sm-2 col-form-label">
				<input type="hidden" name="came_from" value="${came_from}">
				<button class="btn btn-primary" type="submit" name="form.submitted">Save</button>
			</div>
		</div>

		<div class="row">
			<div class="col-sm-2"></div>
			<div class="col-sm-8 assoc-list">
				<div class="pad-top"><p><span class="h4">Participants</span></p></div>
				<table class="table table-sm">
					<thead class="thead-light">
						<tr>
							<th><i class="far fa-trash-alt"></i></th>
							<th>Type</th>
							<th>First name</th>
							<th>Last name</th>
							<th>Phone</th>
						</tr>
					</thead>
					<tbody>
<% count = 0 %>
% for assoc in item.assoc:
<%
person = assoc.person

rowstyle = "row-even" if (count % 2 == 0) else "row-odd"

uurl = request.route_url("admin_person_edit", id=person.id)
%>
						<tr class="${rowstyle}">
							<td><input type="checkbox" name="removeperson" value="${person.id}" ></td>
							<td><a href="${uurl}" class="linkcell">${assoc.type.name}</a></td>
							<td><a href="${uurl}" class="linkcell">${person.firstname}</a></td>
							<td><a href="${uurl}" class="linkcell">${person.lastname}</a></td>
							<td><a href="${uurl}" class="linkcell">${person.phone}</a></td>
						</tr>
<% count += 1 %>\
% endfor
					</tbody>
				</table>
			</div>
			<div class="col-sm-2"></div>
		</div>
% if admin:
		<button type="submit" class="btn btn-danger" name="form.remove">REMOVE Person(s) selected above &amp; Save</button>
% endif
	</form>
</li>
