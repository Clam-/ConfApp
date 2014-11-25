<%inherit file="admin-base.mako"/>
<div class="container">
	<h2>${"Editing" if item.id else "New"} Session</h2>

	<form class="form-horizontal" action="${request.route_url("admin_session_edit", id=item.id) if item.id else request.route_url("admin_session_new")}" method="post">
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formCode">Code (${item.day.description}):</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="code" value="${item.code}" id="formCode"/>
			</div>
			<label class="col-sm-2 control-label" for="formSessionTitle">Session title:</label>
			<div class="col-sm-5">
				<input class="form-control" type="text" name="sesstitle" value="${item.title}" id="formSessionTitle"/>
			</div>
		</div>
	
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formLocation">Location:</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="location" value="${item.location}" id="formLocation"/>
			</div>
			<label class="col-sm-2 control-label" for="formLocType">Location Type:</label>
			<div class="col-sm-5">
				<input class="form-control" type="text" name="loctype" value="${item.loctype}" id="formLocType"/>
			</div>
		</div>

		<div class="form-group">
			<label class="col-sm-2 control-label" for="formHandouts">Handouts (${item.handouts.description}):<br/>Said: ${item.handouts_said.description}</label>
			<div class="col-sm-3">
				${self.selectclslist("handouts", item.handouts, self.attr.HandoutType, _class="form-control", _id="formHandouts")}
			</div>
			<label class="col-sm-2 control-label" for="formEval">Evaluations (${item.evaluations.description}):</label>
			<div class="col-sm-3">
				${self.selectclslist("evaluations", item.evaluations, self.attr.HandoutType, _class="form-control", _id="formEval")}
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formEquipmentBorrowed">Equipment borrowed:</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="equipment" value="${item.equipment}" id="formEquipmentBorrowed"/>
			</div>
			<label class="col-sm-2 control-label" for="formEquipmentReturned">Equipment returned:</label>
			<div class="col-sm-5">
				<input class="form-control" type="text" name="equip_returned" value="${item.equip_returned}" id="formEquipmentReturned"/>
			</div>
		</div>

		<div class="form-group">
			<label class="col-sm-2 control-label" for="formComment">Comment:</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="comments" value="${item.comments}" id="formComment"/>
			</div>
			<label class="col-sm-2 control-label" for="formOther">Other:</label>
			<div class="col-sm-5">
				<input class="form-control" type="text" name="other" value="${item.other}" id="formOther"/>
			</div>
		</div>

<% 
facs = item.facilities_req
faclen = facs.count("\n")
if faclen < 2:
	faclen = 2
%>\
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formFacilitiesReq">Facilities Requested:</label>
			<div class="col-sm-3">
				<textarea class="form-control" name="facilitiesReq" rows="${faclen}" cols="20" id="formFacilitiesReq">${facs}</textarea>
			</div>
<% 
facs = item.facilities_got
faclen = facs.count("\n")
if faclen < 2:
	faclen = 2
%>\
			<label class="col-sm-2 control-label" for="formFacilitiesGot">Facilities Available:</label>
			<div class="col-sm-5">
				<textarea class="form-control" name="facilitiesGot" rows="${faclen}" cols="20" id="formFacilitiesGot">${facs}</textarea>
			</div>
		</div>
		
		<div class="form-group">
			<div class="col-sm-2 control-label">
				<input type="hidden" name="came_from" value="${came_from}"/>
				<input class="btn btn-primary" type="submit" name="form.submitted" value="Save"/>
			</div>
		</div>
				
<% 
sesslen = len(item.assoc)
if sesslen < 2:
	sesslen = 2
%>		
		<div class="form-group">
			<label class="col-sm-2 control-label">People:</label>
			<div class="col-sm-3">
% for assoc in item.assoc:
<% person = assoc.person %>
				<label>
					<input type="checkbox" name="removeperson" value="${person.id}" />
					${person.firstname} ${person.lastname} - ${assoc.type}
				</label>
% endfor
			</div>
		</div>
		
		<div class="form-group">
			<div class="col-sm-2 control-label">
				<input class="btn btn-danger" type="submit" name="form.remove" value="REMOVE Person(s) selected above"/>
			</div>
		</div>
	</form>
</li>