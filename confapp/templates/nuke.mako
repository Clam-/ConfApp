<%inherit file="admin-base.mako"/>
<div class="container">
	<div class="row">
		<h2> Delete all entries </h2>
	</div>
	<div class="row">
	<form action="${request.route_url("nuke")}" method="post" enctype="multipart/form-data">
		<div class="form-group row">
			<label for="nuke">Are you sure you want to remove all entries?</label>
			<button id="nuke" type="submit" class="btn btn-danger">Delete all entries</button>
		</div>
	</form>
	</div>
	<div class="row"> <a class="btn btn-secondary" href="${request.route_url("admin_admin")}" role="button">Cancel</a></p> </div>
</div>