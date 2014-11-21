<%inherit file="admin-base.mako"/>
<div class="container">
	<h2>${"Editing" if item.id else "New"} Person</h2>

	<form class="form-horizontal" action="${request.route_url("admin_person_edit", id=item.id) if item.id else request.route_url("admin_person_new")}" method="post">
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formFirstName">First name:</label>
			<div class="col-sm-5">
				<input class="form-control" type="text" name="firstname" value="${item.firstname}" id="formFirstName"/>
			</div>
		</div>
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formLastName">Last name:</label>
			<div class="col-sm-5">
				<input class="form-control" type="text" name="lastname" value="${item.lastname}" id="formLastName"/>
			</div>
		</div>
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formPhone">Phone:</label>
			<div class="col-sm-5">
				<textarea class="form-control" name="phone" rows="2" cols="20" id="formPhone">${item.phone}</textarea>
			</div>
		</div>
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formEmail">Email:</label>
			<div class="col-sm-5">
				<textarea class="form-control" name="email" rows="2" cols="20" id="formEmail">${item.email}</textarea>
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
			<label class="col-sm-2 control-label">Sessions:</label>
			<div class="col-sm-5">
% for assoc in item.assoc:
<% session = assoc.session %>
				<label>
					<input type="checkbox" name="removesess" value="${session.id}" />
					${session.code} - ${assoc.type} - ${session.title}
				</label>
% endfor
			</div>
		</div>
		<div class="form-group">
			<div class="col-sm-2 control-label">
				<input class="btn btn-danger" type="submit" name="form.remove" value="REMOVE Session(s) selected above"/>
			</div>
		</div>

		<div class="form-group">
			<label class="col-sm-2 control-label" for="formAddSess">Add session (enter code AND type):</label>
			<div class="col-sm-5"><input class="form-control" type="text" name="addsession" value="" id="formAddSess" placeholder="Code"/></div>
		</div>
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formAddType">Type:</label>
			<div class="col-sm-5">${self.selectclslist("type", "", self.attr.PersonType, _class="form-control", _id="formAddType")}</div>
		</div>
		
		<div class="form-group">
			<div class="col-sm-2 control-label">
				<input type="hidden" name="came_from" value="${came_from}"/>
				<input class="btn btn-primary" type="submit" name="form.submitted" value="Save"/>
			</div>
		</div>
	</form>
</div>