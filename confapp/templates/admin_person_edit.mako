<%inherit file="admin-base.mako"/>\
<%page args="mainen, sporten, admin"/>\
<div class="container">
	<div class="header">
		<h2><span>${"Editing" if item.id else "New"} Person</span>
% if item.id and admin:
		<a href="${request.route_url("admin_del", type=item.__tablename__, id=item.id)}" class="btn btn-danger pull-right" role="button">Delete ${type(item).__name__}</a>
% endif
		</h2>
	</div>
	<form class="form-horizontal" action="${request.route_url("admin_person_edit", id=item.id) if item.id else request.route_url("admin_person_new")}" method="post">
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formFirstName">First name</label>
			<div class="col-sm-5">
				<input class="form-control" type="text" name="firstname" value="${item.firstname}" id="formFirstName"/>
				<input type="hidden" name="firstname_orig" value="${item.firstname}"/>
			</div>
		</div>
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formLastName">Last name</label>
			<div class="col-sm-5">
				<input class="form-control" type="text" name="lastname" value="${item.lastname}" id="formLastName"/>
				<input type="hidden" name="lastname_orig" value="${item.lastname}"/>
			</div>
		</div>
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formPhone">Phone</label>
			<div class="col-sm-5">
				<textarea class="form-control" name="phone" rows="2" cols="20" id="formPhone">${item.phone}</textarea>
				<input type="hidden" name="phone_orig" value="${item.phone}"/>
			</div>
		</div>
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formEmail">Email</label>
			<div class="col-sm-5">
				<textarea class="form-control" name="email" rows="2" cols="20" id="formEmail">${item.email}</textarea>
				<input type="hidden" name="email_orig" value="${item.email}"/>
			</div>
		</div>
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formShirt">Shirt</label>
			<div class="col-sm-2">
				<span class="form-control" id="formShirt" readonly="readonly">${"Eligible" if item.shirt else "Ineligible"}</span>
			</div>
			<label class="col-sm-1 control-label" for="formShirtCollect">Collected</label>
			<div class="col-sm-1">
% if item.shirt:
%  if mainen:
				<input type="checkbox" id="formShirtCollect" name="shirtcollect" value="${item.id}" ${'checked="checked"' if item.shirtcollect else ""} />
				<input type="hidden" name="shirtcollect_orig" value="${",".join([str(item.id)] if item.shirtcollect else [])}"/>
%	else:
				${u"\u2714" if item.shirtcollect else u"\u2717"}
%   endif
% endif
			</div>
			<label class="col-sm-1 control-label" for="formShirtSize">Size</label>
			<div class="col-sm-2">
				<span class="form-control" id="formShirtSize" readonly="readonly">${item.shirtsize}</span>
			</div>
		</div>

		<div class="form-group">
			<div class="col-sm-2 control-label">
				<input type="hidden" name="came_from" value="${came_from}"/>
				<button class="btn btn-primary" type="submit" name="form.submitted">Save</button>
			</div>
		</div>

		<div class="form-group">
			<label class="col-sm-2 control-label" for="formAddSess">Add session (enter code AND type)</label>
			<div class="col-sm-5"><input class="form-control" type="text" name="addsession" value="" id="formAddSess" placeholder="Code"/></div>
		</div>
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formAddType">Type</label>
			<div class="col-sm-5">${self.selectclslist("type", "", self.attr.PersonType, _class="form-control", _id="formAddType")}</div>
		</div>
		
		<div class="form-group">
			<div class="col-sm-2 control-label">
				<input type="hidden" name="came_from" value="${came_from}"/>
				<button class="btn btn-primary" type="submit" name="form.submitted">Add &amp; Save </button>
			</div>
		</div>

		<div class="row">
			<div class="col-sm-2"></div>
			<div class="col-sm-8 assoc-list">
				<div class="pad-top"><p><span class="h4">Sessions</span></p></div>
				<table class="table">
					<thead class="table-header">
						<tr>
							<th><span class="glyphicon glyphicon-trash"><span class="sr-only">Trash</span></span></th>
							<th>Type</th>
							<th>Code</th>
							<th>Session name</th>
						</tr>
					</thead>
					<tbody>
<% count = 0 %>
% for assoc in item.assoc:
<% 
session = assoc.session

rowstyle = "row-even" if (count % 2 == 0) else "row-odd"

uurl = request.route_url("admin_session_edit", id=session.id)
%>
						<tr class="${rowstyle}">
							<td><input type="checkbox" name="removesess" value="${session.id}" /></td>
							<td><a href="${uurl}" class="linkcell">${assoc.type}</a></td>
							<td><a href="${uurl}" class="linkcell">${session.code}</a></td>
							<td><a href="${uurl}" class="linkcell">${"<s>" if session.cancelled else "" | n}${session.title}${"</s>" if session.cancelled else "" | n}</a></td>
						</tr>
<% count += 1 %>\
% endfor
					</tbody>
				</table>
			</div>
			<div class="col-sm-2"></div>
		</div>
% if admin:
		<div class="form-group">
			<div class="col-sm-2 control-label">
				<button class="btn btn-danger" type="submit" name="form.remove">Remove Session(s) selected above &amp; Save"</button>
			</div>
		</div>
% endif
	</form>
</div>