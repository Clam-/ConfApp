<%inherit file="admin-base.mako"/>
<div class="container">
	<h2>Editing Entry</h2>
	<form class="form-horizontal" action="${request.route_url("admin_day_edit", day=section, session=session.id, person=person.id)}" method="post">
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formFirstName">First name:</label>
			<div class="col-sm-4">
				<input class="form-control" type="text" name="firstname" value="${person.firstname}" id="formFirstName"/>
			</div>
			<label class="col-sm-2 control-label" for="formLastName">Last name:</label>
			<div class="col-sm-4">
				<input class="form-control" type="text" name="lastname" value="${person.lastname}" id="formLastName"/>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formType">Type (${item.type.description if item.type else ""}):</label>
			<div class="col-sm-4">
				${self.selectclslist("type", item.type, self.attr.PersonType, _class="form-control", _id="formType")}
			</div>
			<label class="col-sm-2 control-label">Code:</label>
			<div class="col-sm-4">
				<p class="form-control-static">${session.code}</p>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formLocation">Location:</label>
			<div class="col-sm-4">
				<input class="form-control" type="text" name="location" value="${session.location}" id="formLocation"/>
			</div>
			<label class="col-sm-2 control-label" for="formSessionTitle">Session title:</label>
			<div class="col-sm-4">
				<input class="form-control" type="text" name="sesstitle" value="${session.title}" id="formSessionTitle"/>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formHandouts">Handouts (${session.handouts.description if session.handouts else ""}):</label>
			<div class="col-sm-4">
				${self.selectclslist("handouts", session.handouts, self.attr.HandoutType, _class="form-control", _id="formHandouts")}
			</div>
			<label class="col-sm-2 control-label" for="formLocType">Location Type:</label>
			<div class="col-sm-4">
				<input class="form-control" type="text" name="loctype" value="${session.loctype}" id="formLocType"/>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formEval">Evaluations (${session.evaluations.description if session.evaluations else ""}):</label>
			<div class="col-sm-4">
				${self.selectclslist("evaluations", session.evaluations, self.attr.HandoutType, _class="form-control", _id="formEval")}
			</div>
			<label class="col-sm-2 control-label" for="formComment">Comment:</label>
			<div class="col-sm-4">
				<input class="form-control" type="text" name="comments" value="${session.comments}" id="formComment"/>
			</div>
		</div>

		<div class="form-group">
			<label class="col-sm-2 control-label" for="formRegistered"><strong>REGISTERED:</strong></label>
			<div class="col-sm-4 ">
				<label class="checkbox-inline">
					<input type="hidden" name="registered" value="_" />
					<input id="formRegistered" type="checkbox" name="registered" value="True" ${'checked="checked"' if item.registered else ""} />
				</label>
			</div>
			<label class="col-sm-2 control-label"><strong>HELPER:</strong></label>
			<div class="col-sm-4">
				${self.selectidlist("helper", helpers, "firstname", "Select Helper")}
			</div>
		</div>
		
		<div class="form-group">
			<div class="col-sm-2 control-label">
				<input type="hidden" name="name" value="${name}"/>
				<input type="hidden" name="code" value="${code}"/>
				<input class="btn btn-primary" type="submit" name="form.submitted" value="Save"/>
			</div>
		</div>

<% 
facs = session.facilities.split("\n")
faclen = len(facs)
if faclen < 2:
	faclen = 2
%>
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formFacilities">Facilities:</label>
			<div class="col-sm-4">
				<select id="formFacilities" class="form-control" name="facilities" size="${faclen}">
				% for fac in facs:
					<option value="ignore">${fac}</option>
				% endfor
				</select>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label">Day:</label>
			<div class="col-sm-4">
				<p class="form-control-static">${session.day}</p>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formEquipmentBorrowed">Equipment borrowed:</label>
			<div class="col-sm-4">
				<input class="form-control" type="text" name="equipment" value="${session.equipment}" id="formEquipmentBorrowed"/>
			</div>
		</div>
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formEquipmentReturned">Equipment returned:</label>
			<div class="col-sm-4">
				<input class="form-control" type="text" name="equip_returned" value="${session.equip_returned}" id="formEquipmentReturned"/>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formPhone">Phone:</label>
			<div class="col-sm-4">
				<textarea class="form-control" name="phone" rows="2" cols="20" id="formPhone">${person.phone}</textarea>
			</div>
		</div>
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formEmail">Email:</label>
			<div class="col-sm-4">
				<textarea class="form-control" name="email" rows="2" cols="20" id="formEmail">${person.email}</textarea>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formOther">Other:</label>
			<div class="col-sm-4">
				<input class="form-control" type="text" name="other" value="${session.other}" id="formOther"/>
			</div>
		</div>
		
		<div class="form-group">
			<div class="col-sm-2 control-label">
				<input class="btn btn-primary" type="submit" name="form.submitted" value="Save"/>
			</div>
		</div>
		
	</form>
</div>