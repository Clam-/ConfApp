<%inherit file="admin-base.mako"/>
<div class="container">
	<div class="row">
		<h2> Admin options </h2>
	</div>
	<div class="row">
		<form action="${request.route_url("settings")}" method="post">
			<div class="form-group row">
				<div class="form-check form-check-inline">
					<input id="evals" class="form-check-input" type="checkbox" name="evals" value="evals" ${'checked="checked"' if settings.evals else ""} >
					<label for="evals" class="form-check-label">Show Evals</label>
				</div>
				<div class="form-check form-check-inline">
					<input id="handouts" class="form-check-input" type="checkbox" name="handouts" value="handouts" ${'checked="checked"' if settings.handouts else ""} >
					<label for="handouts" class="form-check-label">Show Handouts</label>
				</div>
				<div class="form-check form-check-inline">
					<input id="helpers" class="form-check-input" type="checkbox" name="helpers" value="helpers" ${'checked="checked"' if settings.helpers else ""} >
					<label for="helpers" class="form-check-label">Show Helpers</label>
				</div>
			</div>
			<button type="submit" class="btn btn-primary">Save</button>
		</form>
	</div>
	<div class="row">
		<form action="${request.route_url("upload")}" method="post" enctype="multipart/form-data">
			<div class="form-group row">
				<label for="utype">Upload type</label>
				<select class="form-control" name="uploadtype" id="utype">
					<option value="sessionlocs">Sessions, Locations and numbers (update/add new)</option>
					<option value="people">Registration List (will update if Reg ID is used, otherwise add always)</option>
					<option value="shirts">Shirt Qualifiers (update/add new people) (Not yet implemented)</option>
					<option value="hosts">Hosts</option>
					<option value="handouts">Handouts (not yet implemented)</option>
					<option value="cancelled">Cancelled/update venue sessions</option>
				</select>
			</div>
			<div class="form-group row">
				<ul id="csvfields"></ul>
			</div>
			<div class="form-group row">
				<ul id="csvfields2"></ul>
			</div>
			<div class="form-group row">
				<label for="file2">File upload</label>
				<input type="file" class="form-control-file" id="file2" name="csvfile" accept=".csv" onchange="handleFiles(this.files)">
				<small id="upload" class="form-text text-muted">CSV UTF-8 (Comma Delimited) only. Rows in csv will be added alongside existing entries, unless "update" type is selected.</small>
			</div>
			<button type="submit" class="btn btn-primary">Upload</button>
		</form>
	</div>
	<div class="row">
		<form class="form-inline" action="${request.route_url("admin_timecode_new")}" method="post">
			<label class="form-input-label" for="codePrefix">Code Prefix</label>
			<input class="form-control mb-2 mr-sm-2" id="codePrefix" type="text" name="codePrefix" value="" placeholder="(e.g. A, D, FP)" autofocus>
			<label class="form-input-label" for="time">Day</label>
			${self.selectclslist("day", "T", self.attr.DayType, _class="form-control mb-2 mr-sm-2", _id="day")}
			<label class="form-input-label" for="time">Time</label>
			<input class="form-control mb-2 mr-sm-2" id="time" type="text" name="time" value="" placeholder="e.g. 9:00-12:00PM">
			<button type="submit" class="col-1 btn btn-primary" name="form.submitted">Add timeprefix</button>
		</div>
		<div class="row">
			<table class="table table-sm">
				<thead class="thead-light">
					<tr>
						<th>Code Prefix</th>
						<th>Time</th>
						<th>Day</th>
						<th>Delete</th>
					</tr>
				</thead>
				<tbody>
% for item in timecodes:
					<tr>
						<td>${item.prefix}</td>
						<td>${item.time}</td>
						<td>${item.day}</td>
						<td><a href="${request.route_url("admin_timecode_delete", id=item.id)}" class="linkcell" style="color:#AA3939">${u"\u2717"}</a></td>
					</tr>
% endfor
		</tbody>
</div>
<div class="row"> <a class="btn btn-danger" href="${request.route_url("nuke")}" role="button">Clear all entries</a></p> </div>
</div>
<script src="/files/js/uploadData.js"></script>
