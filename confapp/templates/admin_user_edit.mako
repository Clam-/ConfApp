<%inherit file="admin-base.mako"/>\
<%page args="mainen, sporten, admin"/>\
<div class="container">
	<div class="header">
		<h2><span>${"Editing" if item.id else "New"} User</span>
% if item.id:
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
			<label for="formUsername">username</label>
			<input class="form-control" type="text" name="username" value="${item.username}" id="formUsername" >
			<input type="hidden" name="username_orig" value="${item.username}">
		</div>
		<div class="form-group row">
			<label for="formName">Name</label>
			<input class="form-control" type="text" name="name" value="${item.name}" id="formName">
			<input type="hidden" name="name_orig" value="${item.name}">
		</div>
	
		<div class="form-group row">
			<label for="formRole">Role</label>
			${self.selectclslist("role", item.role if item.role else self.attr.UserRole.none, self.attr.UserRole, _class="form-control", _id="formRole")}
			<input type="hidden" name="role_orig" value="${item.role.value if item.role else self.attr.UserRole.none.value}">
		</div>
		<div class="form-group row">
			<label for="formLastseen">Last seen</label>
			<span class="form-control utcdate" id="formLastseen" readonly="readonly">${item.lastseen}</span>
		</div>
		<div class="form-group row">
			<label for="formPassword">Set password</label>
			<input class="form-control" type="password" name="password" value="" id="formPassword" >
		</div>

		<input type="hidden" name="came_from" value="${came_from}">
		<button class="btn btn-primary" type="submit" name="form.submitted">Save</button>
	</form>
</li>