<%inherit file="admin-base.mako"/>
<div class="container">
	<div class="header">
		<h2><span>${"Editing" if item.id else "New"} Session</span>
% if item.id:
		<a href="${request.route_url("admin_del", type=item.__tablename__, id=item.id)}" class="btn btn-danger pull-right" role="button">Delete ${type(item).__name__}</a>
% endif
		</h2>
	</div>
	<form class="form-horizontal" action="${request.route_url("admin_session_edit", id=item.id) if item.id else request.route_url("admin_session_new")}" method="post">
		
		<div class="form-group">
			<label class="col-sm-1 control-label" for="formCode">Code</label>
			<div class="col-sm-1">
				<input class="form-control" type="text" name="code" value="${item.code}" id="formCode"/>
				<input type="hidden" name="code_orig" value="${item.code}"/>
			</div>
			<label class="col-sm-1 control-label" for="formDay">Day</label>
			<div class="col-sm-2">
				${self.selectclslist("day", item.day, self.attr.DayType, _class="form-control", _id="formDay")}
				<input type="hidden" name="day_orig" value="${item.day.value}"/>
			</div>
			<label class="col-sm-2 control-label" for="formSessionTitle">Session title</label>
			<div class="col-sm-5">
				<input class="form-control" type="text" name="title" value="${item.title}" id="formSessionTitle"/>
				<input type="hidden" name="title_orig" value="${item.title}"/>
			</div>
		</div>
	
		<div class="form-group">
			<label class="col-sm-1 control-label" for="formBuilding">Building</label>
			<div class="col-sm-1">
				<input class="form-control" type="text" name="building" value="${item.building}" id="formBuilding"/>
				<input type="hidden" name="building_orig" value="${item.building}"/>
			</div>
			<label class="col-sm-1 control-label" for="formRoom">Room</label>
			<div class="col-sm-4">
				<input class="form-control" type="text" name="room" value="${item.room}" id="formRoom"/>
				<input type="hidden" name="room_orig" value="${item.room}"/>
			</div>
			<label class="col-sm-2 control-label" for="formLocType">Location Type</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="loctype" value="${item.loctype}" id="formLocType"/>
				<input type="hidden" name="loctype_orig" value="${item.loctype}"/>
			</div>
		</div>

		<div class="form-group">
			<label class="col-sm-2 control-label" for="formHandouts">Handouts (Said: ${item.handouts_said.description})</label>
			<div class="col-sm-3">
				${self.selectclslist("handouts", item.handouts, self.attr.HandoutType, _class="form-control", _id="formHandouts")}
				<input type="hidden" name="handouts_orig" value="${item.handouts.value}"/>
			</div>
			<label class="col-sm-2 control-label" for="formEval">Evaluations (${item.evaluations.description})</label>
			<div class="col-sm-3">
				${self.selectclslist("evaluations", item.evaluations, self.attr.HandoutType, _class="form-control", _id="formEval")}
				<input type="hidden" name="evaluations_orig" value="${item.evaluations.value}"/>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formEquipmentBorrowed">Equipment borrowed</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="equipment" value="${item.equipment}" id="formEquipmentBorrowed"/>
				<input type="hidden" name="equipment_orig" value="${item.equipment}"/>
			</div>
			<label class="col-sm-2 control-label" for="formEquipmentReturned">Equipment returned</label>
			<div class="col-sm-5">
				<input class="form-control" type="text" name="equip_returned" value="${item.equip_returned}" id="formEquipmentReturned"/>
				<input type="hidden" name="equip_returned_orig" value="${item.equip_returned}"/>
			</div>
		</div>

		<div class="form-group">
			<label class="col-sm-2 control-label" for="formComment">Comment</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="comments" value="${item.comments}" id="formComment"/>
				<input type="hidden" name="comments_orig" value="${item.comments}"/>
			</div>
			<label class="col-sm-2 control-label" for="formOther">Other</label>
			<div class="col-sm-5">
				<input class="form-control" type="text" name="other" value="${item.other}" id="formOther"/>
				<input type="hidden" name="other_orig" value="${item.other}"/>
			</div>
		</div>

<% 
facs = item.facilities_req
faclen = facs.count("\n")
if faclen < 2:
	faclen = 2
%>\
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formFacilitiesReq">Facilities Requested</label>
			<div class="col-sm-3">
				<textarea class="form-control" name="facilities_req" rows="${faclen}" cols="20" id="formFacilitiesReq">${facs}</textarea>
				<input type="hidden" name="facilities_req_orig" value="${item.facilities_req}"/>
			</div>
<% 
facs = item.facilities_got
faclen = facs.count("\n")
if faclen < 2:
	faclen = 2
%>\
			<label class="col-sm-2 control-label" for="formFacilitiesGot">Facilities Available</label>
			<div class="col-sm-5">
				<textarea class="form-control" name="facilities_got" rows="${faclen}" cols="20" id="formFacilitiesGot">${facs}</textarea>
				<input type="hidden" name="facilities_got_orig" value="${item.facilities_got}"/>
			</div>
		</div>
		
		<div class="form-group">
			<div class="col-sm-2 control-label">
				<input type="hidden" name="came_from" value="${came_from}"/>
				<button class="btn btn-primary" type="submit" name="form.submitted">Save</button>
			</div>
		</div>
		
		<div class="row">
			<div class="col-sm-2"></div>
			<div class="col-sm-8 assoc-list">
				<div class="pad-top"><p><span class="h4">Participants</span></p></div>
				<table class="table">
					<thead class="table-header">
						<tr>
							<th><span class="glyphicon glyphicon-trash"><span class="sr-only">Trash</span></span></th>
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
							<td><input type="checkbox" name="removeperson" value="${person.id}" /></td>
							<td><a href="${uurl}" class="linkcell">${assoc.type}</a></td>
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
		<button type="submit" class="btn btn-danger" name="form.remove">REMOVE Person(s) selected above &amp; Save</button>
	</form>
</li>