<%inherit file="admin-base.mako"/>
<div class="container">
	<h2>Please log in</h2>
	<p class="text-danger">${message}</p>
	<form class="form-horizontal" action="${url}" method="post">
		<div class="form-group">
			<label class="col-sm-3 control-label" for="formUsername">Username</label>
			<div class="col-sm-3">
				<input class="form-control" type="text" name="username" value="${username}" id="formUsername" autofocus />
			</div>
		</div>
		<div class="form-group">
			<label class="col-sm-3 control-label" for="formPassword">Password</label>
			<div class="col-sm-3">
				<input class="form-control" type="password" name="password" value="${password}" id="formPassword"/>
			</div>
		</div>
		
		<div class="form-group">
			<div class="col-sm-2">
				<input type="hidden" name="came_from" value="${came_from}"/>
				<button class="btn btn-primary" type="submit" name="form.submitted">Log In</button>
			</div>
		</div>
	</form>
</div>