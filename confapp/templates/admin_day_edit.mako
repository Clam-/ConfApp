<%inherit file="admin-base.mako"/>
<div class="container">
	<h3>Editing Check-in for ${section}</h3>
	<form class="form-horizontal" action="${request.route_url("admin_day_edit", day=section, session=session.id, person=person.id)}" method="post">
		<div class="form-group">
			<label class="col-sm-2 control-label">Code:</label>
			<div class="col-sm-3">
				<p class="form-control-static">${session.code}</p>
			</div>
			<label class="col-sm-2 control-label">Session title:</label>
			<div class="col-sm-5">
				<p class="form-control-static">${session.title}</p>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label">Location:</label>
			<div class="col-sm-3">
				<p class="form-control-static">${session.location}</p>
			</div>
			<label class="col-sm-2 control-label">Location Type:</label>
			<div class="col-sm-5">
				<p class="form-control-static">${session.loctype}</p>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formHandouts">Handouts (${session.handouts.description}):<br/>Said: ${session.handouts_said.description}</label>
			<div class="col-sm-3">
				${self.selectclslist("handouts", session.handouts, self.attr.HandoutType, _class="form-control", _id="formHandouts")}
			</div>
			<label class="col-sm-2 control-label" for="formEval">Evaluations (${session.evaluations.description}):</label>
			<div class="col-sm-3">
				${self.selectclslist("evaluations", session.evaluations, self.attr.HandoutType, _class="form-control", _id="formEval")}
			</div>
			
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formComment">Comment:</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="comments" value="${session.comments}" id="formComment"/>
			</div>
			<label class="col-sm-2 control-label" for="formHelper"><strong>HELPER:</strong></label>
			<div class="col-sm-3">
				${self.selectidlist("helper", helpers, ("firstname", "lastname"), "Select Helper", _class="form-control", _id="formHelper")}
			</div>
			
		</div>

		<div class="form-group">
			<label class="col-sm-2 control-label" for="formPhone">Participants:</label>
		</div>
		<div class="row">
			<div class="col-sm-2"></div>
			<div class="col-sm-9">
			<table class="table">
				<thead class="table-header">
					<tr>
						<th> Reg&rsquo;d </th>
						<th> Last name </th>
						<th> First name </th>
						<th> Type </th>
					</tr>
				</thead>
<% count = 0 %>
% for assoc in assocs:
<%
iperson = assoc.person
if iperson is person:
	style = "marker markercolor"
else:
	style = "session sessioneven" if (count % 2 == 0) else "session sessionodd"
person_id = iperson.id
uurl = request.route_url("admin_person_edit", id=person_id)
%>\
				<tr>
					<td class="${style}"><input type="checkbox" name="registered" value="${person_id}" ${'checked="checked"' if assoc.registered else ""} /> </td>
					<td class="${style}"><a href="${uurl}" class="linkcell">${iperson.lastname}</a></td>
					<td class="${style}"><a href="${uurl}" class="linkcell">${iperson.firstname}</a></td>
					<td class="${style}"><a href="${uurl}" class="linkcell">${assoc.type}</a></td>
				</tr>
<% count += 1 %>\
% endfor
			</table></div>
			<div class="col-sm-1"></div>
		</div>
		
		<div class="form-group">
			<div class="col-sm-2 control-label">
				<input type="hidden" name="name" value="${name}"/>
				<input type="hidden" name="code" value="${code}"/>
				<input class="btn btn-primary" type="submit" name="form.submitted" value="Save"/>
			</div>
			<div class="col-sm-1 control-label">
				<input class="btn btn-default" type="submit" name="form.cancelled" value="Cancel"/>
			</div>
		</div>

<% 
facs = session.facilities_req.split("\n")
faclen = len(facs)
if faclen < 2:
	faclen = 2
%>
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formFacilities">Facilities Requested:</label>
			<div class="col-sm-3">
				<select id="formFacilities" class="form-control" name="facilities" size="${faclen}">
				% for fac in facs:
					<option value="ignore">${fac}</option>
				% endfor
				</select>
			</div>
<% 
facs = session.facilities_got.split("\n")
faclen = len(facs)
if faclen < 2:
	faclen = 2
%>
		<label class="col-sm-2 control-label" for="formFacilities">Facilities Available:</label>
			<div class="col-sm-3">
				<select id="formFacilities" class="form-control" name="facilities" size="${faclen}">
				% for fac in facs:
					<option value="ignore">${fac}</option>
				% endfor
				</select>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formEquipmentBorrowed">Equipment borrowed:</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="equipment" value="${session.equipment}" id="formEquipmentBorrowed"/>
			</div>
			<label class="col-sm-2 control-label" for="formEquipmentReturned">Equipment returned:</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="equip_returned" value="${session.equip_returned}" id="formEquipmentReturned"/>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formOther">Other:</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="other" value="${session.other}" id="formOther"/>
			</div>
		</div>
		
		<div class="form-group">
			<div class="col-sm-2 control-label">
				<input class="btn btn-primary" type="submit" name="form.submitted" value="Save"/>
			</div>
			<div class="col-sm-1 control-label">
				<input class="btn btn-default" type="submit" name="form.cancelled" value="Cancel"/>
			</div>
		</div>
		
	</form>
</div>