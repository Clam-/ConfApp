<%inherit file="admin-base.mako"/>
<div class="container">
	<h2>${"Editing" if item.id else "New"} Helper</h2>

	<form class="form-horizontal" action="${request.route_url("admin_helper_edit", id=item.id) if item.id else request.route_url("admin_helper_new")}" method="post">
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
				<input class="form-control" type="text" name="phone" value="${item.phone}" id="formPhone"/>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formAway">Away:</label>
			<div class="col-sm-4 ">
				<label class="checkbox-inline">
					<input type="hidden" name="away" value="_" />
					<input id="formAway" type="checkbox" name="away" value="True" ${'checked="checked"' if item.away else ""} />
				</label>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formComment">Comment:</label>
			<div class="col-sm-5">
				<input class="form-control" type="text" name="comment" value="${item.comment}" id="formComment"/>
			</div>
		</div>

		<div class="form-group">
			<div class="col-sm-2 control-label">
				<input type="hidden" name="came_from" value="${came_from}"/>
				<input class="btn btn-primary" type="submit" name="form.submitted" value="Save"/>
			</div>
		</div>
	</form>
	<div class="form-group">
% if item.session:
		<label class="col-sm-2 control-label">At session:</label>
		<div class="col-sm-5">
			<label>
<% session = item.session %>
					${session.code} - ${session.location} - ${session.title}
			</label>
		</div>
% else:
	<label class="col-sm-2 control-label">Not at a session.</label>
% endif
	</div>
</div>