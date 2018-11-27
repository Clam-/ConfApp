<%inherit file="admin-base.mako"/>\
<%page args="mainen, sporten, admin"/>\
<!--
<script type="text/javascript" src="/files/js/sidebar.js"></script>
-->
<div class="container-fluid">
<div class="col-sm-12">
	<h3>Editing Check-in for ${section}</h3>
	<form class="form-horizontal" action="${request.route_url("admin_day_edit", day=section, session=session.id, person=person.id)}" method="post">
		<div class="form-group">
			<label class="col-sm-2 control-label">Code</label>
			<div class="col-sm-3">
				<p class="form-control-static">${session.code}</p>
			</div>
			<label class="col-sm-2 control-label">Session title</label>
			<div class="col-sm-5">
				<p class="form-control-static">${session.title}</p>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label">Building</label>
			<div class="col-sm-1">
				<p class="form-control-static">${session.room.building.number if session.room else "Error."}</p>
			</div>

			<label class="col-sm-1 control-label">Address</label>
			<div class="col-sm-2">
				<p class="form-control-static">${session.room.building.address if session.room else "Error."}</p>
			</div>
			<label class="col-sm-1 control-label">Room</label>
			<div class="col-sm-4">
				<p class="form-control-static">${session.room.name if session.room else "Error."}</p>
			</div>
		</div>
		
		<div class="form-group">
% if not mainen:
			<label class="col-sm-2 control-label">Handouts <br/>(Said: ${session.handouts_said.description})</label>
				<p class="col-sm-3 form-control-static">${str(session.handouts)}</p>
			<label class="col-sm-2 control-label">Evaluations</label>
				<p class="col-sm-3 form-control-static">${session.evaluations.description}</p>
% else:
			<label class="col-sm-2 control-label" for="formHandouts">Handouts (${session.handouts.description}):<br/>Said: ${session.handouts_said.description}</label>
			<div class="col-sm-3">
				${self.selectclslist("handouts", session.handouts, self.attr.HandoutType, _class="form-control", _id="formHandouts")}
				<input type="hidden" name="handouts_orig" value="${session.handouts.value}"/>
			</div>
			<label class="col-sm-2 control-label" for="formEval">Evaluations (${session.evaluations.description})</label>
			<div class="col-sm-3">
				${self.selectclslist("evaluations", session.evaluations, self.attr.HandoutType, _class="form-control", _id="formEval")}
				<input type="hidden" name="evaluations_orig" value="${session.evaluations.value}"/>
			</div>
% endif
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formComment">Comment</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="comments" value="${session.comments}" id="formComment"/>
				<input type="hidden" name="comments_orig" value="${session.comments}"/>
			</div>
% if helpers_show and mainen:
			<label class="col-sm-2 control-label" for="formHelper"><strong>HELPER:</strong></label>
			<div class="col-sm-3">
				${self.selectidlist("helper", helpers, ("firstname", "lastname"), "Select Helper", _class="form-control", _id="formHelper")}
			</div>
% endif
		</div>

		<div class="row">
			<div class="col-sm-2"></div>
			<div class="col-sm-8 assoc-list">
				<div class="pad-top"><p><span class="h4">Participants</span> <span class="h5">(Click checkbox and click Save to check-in)</span></p></div>
				<table class="table">
					<thead class="table-header">
						<tr>
							<th><abbr title="Main hall registration">Main</th>
							<th><abbr title="Sports Centre registration">Sports</th>
% if mainen:
							<th><abbr title="Eligable for shirt">Shirt</th>
							<th><abbr title="Shirt size (Blank means pick one)">S.Size</th>
% endif
							<th>Last name</th>
							<th>First name</th>
							<th>Type</th>
						</tr>
					</thead>
					<tbody>
<% 
count = 0 
regids = []
regids_sport = []
collectids = []
%>
% for assoc in assocs:
<%
iperson = assoc.person
if iperson is person:
	rowstyle = "row-marker"
else:
	rowstyle = "row-even" if (count % 2 == 0) else "row-odd"
person_id = iperson.id
uurl = request.route_url("admin_person_edit", id=person_id)
if session.room and (session.room.building.number == "1" ): # or session.room.building.number == "60"
	sporttick = u"\u2714" if assoc.registered_sport else u"\u2717"
else:
	sporttick = "-"
	
if assoc.registered:
	regids.append(str(person_id))
if assoc.registered_sport:
	regids_sport.append(str(person_id))
if iperson.shirtcollect:	
	collectids.append(str(person_id))
	
%>\
						<tr class="${rowstyle}">
% if not mainen:
							<td><span class="linkcell ${"text-success" if assoc.registered else "text-muted"}">${u"\u2714" if assoc.registered else u"\u2717"}</span></td>
% else:
							<td><input type="checkbox" name="registered" value="${person_id}" ${'checked="checked"' if assoc.registered else ""} /> </td>
% endif
% if sporttick != "-" and sporten:
							<td><input type="checkbox" name="registered_sport" value="${person_id}" ${'checked="checked"' if assoc.registered_sport else ""} /> </td>
% else:
							<td><span class="linkcell ${"text-success" if assoc.registered_sport else "text-muted"}">${sporttick}</span></td>
% endif
% if mainen:
%  if iperson.shirt:
							<td><input type="checkbox" name="shirtcollect" value="${person_id}" ${'checked="checked"' if iperson.shirtcollect else ""} /> </td>
%  else:
							<td><span class="linkcell">${u"\u2717"}</span></td>
%  endif
							<td><span class="linkcell">${iperson.shirtsize}</a></td>
% endif
							<td><a href="${uurl}" class="linkcell">${iperson.lastname}</a></td>
							<td><a href="${uurl}" class="linkcell">${iperson.firstname}</a></td>
							<td><a href="${uurl}" class="linkcell">${assoc.type}</a></td>
						</tr>
<% count += 1 %>\
% endfor
					</tbody>
				</table>
			</div>
			<div class="col-sm-2">
% if mainen:
				<input type="hidden" name="registered_orig" value="${",".join(regids)}"/>
				<input type="hidden" name="shirtcollect_orig" value="${",".join(collectids)}"/>
% endif
% if sporttick != "-" and sporten:
				<input type="hidden" name="registered_sport_orig" value="${",".join(regids_sport)}"/>
% endif
			</div>
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

		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formEquipmentBorrowed">Equipment borrowed</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="equipment" value="${session.equipment}" id="formEquipmentBorrowed"/>
				<input type="hidden" name="equipment_orig" value="${session.equipment}"/>
			</div>
			<label class="col-sm-2 control-label" for="formEquipmentReturned">Equipment returned</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="equip_returned" value="${session.equip_returned}" id="formEquipmentReturned"/>
				<input type="hidden" name="equip_returned_orig" value="${session.equip_returned}"/>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formOther">Other</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="other" value="${session.other}" id="formOther"/>
				<input type="hidden" name="other_orig" value="${session.other}"/>
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
		
		<div class="form-group">
			<label class="col-sm-2 control-label">Booked</label>
			<div class="col-sm-1">
				<p class="form-control-static">${session.booked if session.booked else ""}</p>
			</div>

			<label class="col-sm-1 control-label">Capacity</label>
			<div class="col-sm-2">
				<p class="form-control-static">${session.max if session.max else ""}</p>
			</div>
		</div>
		
	</form>
</div>
<!--
<div id="sidebar" class="col-xs-2">
	<h3><a href="${request.route_url("admin_helper_list")}">Helpers</a> <a href="#" >&#8635;</a></h3>
	<table class="table">
	</table>
</div>
-->
</div>