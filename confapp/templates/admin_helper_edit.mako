<%inherit file="admin-base.mako"/>
<div class="container">
	<div class="header">
		<h2><span>${"Editing" if item.id else "New"} Helper</span>
% if item.id:
		<a href="${request.route_url("admin_del", type=item.__tablename__, id=item.id)}" class="btn btn-danger pull-right" role="button">Delete ${type(item).__name__}</a>
% endif
		</h2>
	</div>
	<form class="form-horizontal" action="${request.route_url("admin_helper_edit", id=item.id) if item.id else request.route_url("admin_helper_new")}" method="post">
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
				<input class="form-control" type="text" name="phone" value="${item.phone}" id="formPhone"/>
				<input type="hidden" name="phone_orig" value="${item.phone}"/>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formAway">Away</label>
			<div class="col-sm-4 ">
				<label class="checkbox-inline">
					<input type="hidden" name="away" value="_" />
					<input id="formAway" type="checkbox" name="away" value="True" ${'checked="checked"' if item.away else ""} />
					<input type="hidden" name="away_orig" value="${item.away}"/>
				</label>
			</div>
		</div>
		
		<div class="form-group">
			<label class="col-sm-2 control-label" for="formComment">Comment</label>
			<div class="col-sm-5">
				<input class="form-control" type="text" name="comment" value="${item.comment}" id="formComment"/>
				<input type="hidden" name="comment_orig" value="${item.comment}"/>
			</div>
		</div>

		<div class="form-group">
			<div class="col-sm-2 control-label">
				<input type="hidden" name="came_from" value="${came_from}"/>
				<button class="btn btn-primary" type="submit" name="form.submitted">Save</button>
			</div>
		</div>
	</form>
	
	<div class="row">
		<div class="col-sm-2"></div>
		<div class="col-sm-8 assoc-list">
			<div class="pad-top"><p><span class="h4">Location</span></p></div>
			<table class="table">
				<thead class="table-header">
					<tr>
						<th>Building</th>
						<th>Room</th>
						<th>Session code</th>
						<th>Session title</th>
					</tr>
				</thead>
				<tbody>
					<tr class="row-odd">
% if item.session:
<% 
session = item.session 
uurl = request.route_url("admin_session_edit", id=session.id)
%>
						<td><a href="${uurl}" class="linkcell">${session.building}</a></td>
						<td><a href="${uurl}" class="linkcell">${session.room}</a></td>
						<td><a href="${uurl}" class="linkcell">${session.code}</a></td>
						<td><a href="${uurl}" class="linkcell">${session.title}</a></td>
% else:
						<td>-</td><td>-</td><td>-</td><td>-</td>
% endif
					</tr>
				</tbody>
			</table>
		</div>
		<div class="col-sm-2"></div>
	</div>
</div>