<%inherit file="admin-base.mako"/>\
<%page args="mainen, sporten, admin"/>\
<!--
<script type="text/javascript" src="/files/js/sidebar.js"></script>
-->
<div class="container-fluid">
<div class="col-sm-12">
	<h3>Editing Check-in for ${section}</h3>
	<form action="${request.route_url("admin_day_edit", day=section, session=session.id, person=person.id)}" method="post">
		<div class="form-group row">
			<div class="col-2"></div>
			<label class="col-1 col-form-label">Code</label>
			<div class="col-1">
				<input type="text" readonly class="form-control-plaintext" value="${session.code}">
			</div>
			<label class="col-2 col-form-label">Session title</label>
			<div class="col">
				<input type="text" readonly class="form-control-plaintext" value="${session.title}">
			</div>
			<div class="col-2"></div>
		</div>

		<div class="form-group row">
			<div class="col-2"></div>
			<label class="col-1 col-form-label">Building</label>
			<div class="col-1">
				<input type="text" readonly class="form-control-plaintext" value="${session.room.building.number if session.room else "Error."}">
			</div>

			<div class="col">
				<input type="text" readonly class="form-control-plaintext" value="${session.room.building.name if session.room else "Error."}">
			</div>
			<label class="col-1 col-form-label">Room</label>
			<div class="col-2">
				<input type="text" readonly class="form-control-plaintext" value="${session.room.name if session.room else "Error."}">
			</div>
			<div class="col-2"></div>
		</div>

		<div class="form-group row">
			<div class="col-2"></div>
% if not mainen:
			<label class="col col-form-label">Handouts <br>(Said: ${session.handouts_said.name})</label>
			<input type="text" readonly class="col-1 form-control-plaintext" value="${session.handouts.name}">
			<label class="col-1 col-form-label">Evaluations</label>
			<input type="text" readonly class="col-1 form-control-plaintext" value="${session.evaluations.name}">
% else:
			<label class="col col-form-label" for="formHandouts">Handouts (${session.handouts.name}):<br>Said: ${session.handouts_said.name}</label>
			<div class="col-2">
				${self.selectclslist("handouts", session.handouts, self.attr.HandoutType, _class="form-control", _id="formHandouts")}
				<input type="hidden" name="handouts_orig" value="${session.handouts.value}">
			</div>
			<label class="col col-form-label" for="formEval">Evaluations (${session.evaluations.name})</label>
			<div class="col-2">
				${self.selectclslist("evaluations", session.evaluations, self.attr.HandoutType, _class="form-control", _id="formEval")}
				<input type="hidden" name="evaluations_orig" value="${session.evaluations.value}">
			</div>
% endif
			<div class="col-2"></div>
		</div>

		<div class="form-group row">
			<div class="col-2"></div>
			<label class="col-2 col-form-label" for="formComment">Session Comment</label>
			<div class="col">
				<input class="form-control" type="text" name="comments" value="${session.comments}" id="formComment">
				<input type="hidden" name="comments_orig" value="${session.comments}">
			</div>
		<div class="col-2"></div>
		</div>

		<div class="row">
			<div class="col-sm-2"></div>
			<div class="col-sm-8 assoc-list">
				<div class="pad-top"><p><span class="h4">Participants</span> <span class="h5">(Click checkbox and click Save to check-in)</span></p></div>
				<table class="table table-sm">
					<thead class="thead-light">
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
if session.sport:
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
							<td>
								<div class="custom-control custom-checkbox">
								  <input id="m${person_id}" class="custom-control-input" type="checkbox" name="registered" value="${person_id}" ${'checked="checked"' if assoc.registered else ""} >
								  <label class="custom-control-label" for="m${person_id}"></label>
								</div>
							</td>
% endif
% if session.sport and sporten:
							<td>
								<div class="custom-control custom-checkbox">
									<input id="s${person_id}" class="custom-control-input" type="checkbox" name="registered_sport" value="${person_id}" ${'checked="checked"' if assoc.registered_sport else ""} >
									<label class="custom-control-label" for="s${person_id}"></label>
								</div>
							</td>
% else:
							<td><span class="linkcell ${"text-success" if assoc.registered_sport else "text-muted"}">${sporttick}</span></td>
% endif
% if mainen:
%  if iperson.shirt:
							<td>
								<div class="custom-control custom-checkbox">
									<input id="t${person_id}" class="custom-control-input" type="checkbox" name="shirtcollect" value="${person_id}" ${'checked="checked"' if iperson.shirtcollect else ""} >
									<label class="custom-control-label" for="t${person_id}"></label>
								</div>
							</td>
%  else:
							<td><span class="linkcell">${u"\u2717"}</span></td>
%  endif
							<td><span class="linkcell">${iperson.shirtsize}</a></td>
% endif
							<td><a href="${uurl}" class="linkcell"><abbr title="${iperson.phone}">${iperson.lastname}</abbr></a></td>
							<td><a href="${uurl}" class="linkcell">${iperson.firstname}</a></td>
							<td><a href="${uurl}" class="linkcell">${assoc.type.name}</a></td>
						</tr>
<% count += 1 %>\
% endfor
					</tbody>
				</table>
			</div>
			<div class="col-sm-2">
% if mainen:
				<input type="hidden" name="registered_orig" value="${",".join(regids)}">
				<input type="hidden" name="shirtcollect_orig" value="${",".join(collectids)}">
% endif
% if sporttick != "-" and sporten:
				<input type="hidden" name="registered_sport_orig" value="${",".join(regids_sport)}">
% endif
			</div>
		</div>
		<div class="form-group row">
			<div class="col-2"></div>
			<div class="col-sm-1 col-form-label">
				<input type="hidden" name="name" value="${name}">
				<input type="hidden" name="code" value="${code}">
				<input class="btn btn-primary" type="submit" name="form.submitted" value="Save">
			</div>
			<div class="col-sm-1 col-form-label">
				<input class="btn btn-secondary" type="submit" name="form.cancelled" value="Cancel">
			</div>
			<div class="col-sm-2 col-form-label">
				<input class="btn btn-info" type="submit" name="form.add" value="Save and Add Person">
			</div>
			<div class="col-2"></div>
		</div>


		<div class="form-group row">
			<div class="col-2"></div>
			<label class="col-sm-2 col-form-label" for="formEquipmentBorrowed">Equipment borrowed</label>
			<div class="col-sm-2">
				<input class="form-control" type="text" name="equipment" value="${session.equipment}" id="formEquipmentBorrowed">
				<input type="hidden" name="equipment_orig" value="${session.equipment}">
			</div>
			<label class="col-sm-2 col-form-label" for="formEquipmentReturned">Equipment returned</label>
			<div class="col-sm-2">
				<input class="form-control" type="text" name="equip_returned" value="${session.equip_returned}" id="formEquipmentReturned">
				<input type="hidden" name="equip_returned_orig" value="${session.equip_returned}">
			</div>
			<div class="col-2"></div>
		</div>

		<div class="form-group row">
			<div class="col-2"></div>
			<label class="col-sm-2 col-form-label" for="formOther">Other</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="other" value="${session.other}" id="formOther">
				<input type="hidden" name="other_orig" value="${session.other}">
			</div>
			<div class="col-2"></div>
		</div>

		<div class="form-group row">
			<div class="col-2"></div>
			<div class="col-sm-2 col-form-label">
				<input class="btn btn-primary" type="submit" name="form.submitted" value="Save">
			</div>
			<div class="col-sm-1 col-form-label">
				<input class="btn btn-secondary" type="submit" name="form.cancelled" value="Cancel">
			</div>
			<div class="col-2"></div>
		</div>

		<div class="form-group row">
			<div class="col-2"></div>
			<label class="col-sm-1 col-form-label">Time</label>
			<div class="col-sm-2">
				<input type="text" readonly class="form-control-plaintext" value="${session.time if session.time else ''}">
			</div>
			<label class="col-sm-2 col-form-label">Booked</label>
			<div class="col-sm-1">
				<input type="text" readonly class="form-control-plaintext" value="${session.booked if session.booked else ''}">
			</div>

			<label class="col-sm-1 col-form-label">Capacity</label>
			<div class="col-sm-2">
				<input type="text" readonly class="form-control-plaintext" value="${session.max if session.max else ''}">
			</div>
			<div class="col-2"></div>
		</div>

	</form>
</div>
</div>
