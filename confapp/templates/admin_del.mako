<%inherit file="admin-base.mako"/>
<div class="container">
	<h2>REMOVE ${item.label()} ?</h2>

	Are you sure you want to remove the ${item.label()} ?
	
	<form action="${request.route_url("admin_del_4real", type=item.__tablename__, id=item.id)}" method="post">
	
		<div class="form-group row">
			<div class="col-sm-2">
				<input type="hidden" name="came_from" value="${came_from}">
				<button class="btn btn-danger" type="submit" name="form.submitted">Remove</button>
			</div>
			<div class="col-sm-2">
				<a href="${came_from}" class="btn btn-primary float-right" role="button">Cancel</a>
			</div>
		</div>
	</form>
</li>