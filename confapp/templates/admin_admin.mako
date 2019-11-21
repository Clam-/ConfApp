<%inherit file="admin-base.mako"/>
<div class="container">
	<div class="row">
		<h2> Admin options </h2>
	</div>
	<div class="row">
	<form action="${request.route_url("upload")}" method="post" enctype="multipart/form-data">
		<div class="form-group row">
			<label for="utype">Upload type</label>
			<select class="form-control" name="uploadtype" id="utype">
				<option value="sessionlocs">Sessions and Locations</option>
				<option value="sessionscaps">Capacities</option>
				<option value="people">Registration List</option>
				<option value="shirts">Separate Shirt List</option>
				<option value="hosts1">Hosts</option>
				<option value="hosts3">Hosts Feature</option>
				<option value="peopleex">Extra people</option>
				<option value="handouts">Handouts</option>
				<option value="cancelled">CANCELLED</option>
			</select>
		</div>
		<div class="form-group row">
			<label for="file2">File upload</label>
			<input type="file" class="form-control-file" id="file2" name="csvfile" accept=".csv">
			<small id="upload" class="form-text text-muted">CSV UTF-8 (Comma Delimited) only. Rows in csv will be added alongside existing entries.</small>
		</div>
		<button type="submit" class="btn btn-primary">Upload</button>
	</form>
	</div>
	<div class="row"> <a class="btn btn-danger" href="${request.route_url("nuke")}" role="button">Clear all entries</a></p> </div>
</div>
