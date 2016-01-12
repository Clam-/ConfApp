<%inherit file="admin-base.mako"/>
<% from time import localtime, strftime 
from confapp.libs.helpers import distance_of_time_in_words
TIMEFORMAT = "%H:%M:%S"
%>
<div class="maxbig container">
	<div class="row">
		<div class="col-xs-9">
			<h2>${section.capitalize()} list</h2>
		</div>
		<div class="col-xs-3">
			<h2><a href="${request.route_url("admin_helper_new")}" class="btn btn-primary">New</a></h2>
		</div>
	</div>
	<div class="row">
	<table class="table col-xs-12">
		<thead class="table-header">
			<tr>
				<th> First Name </th>
				<th> Last Name </th>
				<th> Phone </th>
				<th> Time </th>
				<th> Location </th>
				<th> Comment </th>
				<th> Return </th>
			</tr>
		</thead>
<% count = 0 %>
% for item in items:
	<%	
		uurl = request.route_url("admin_helper_edit", id=item.id)
		timecls = " text-success"
		dispatched = item.dispatched
		returned = item.returned
		longtime = None
		itime = None
		namecls = ""
		if item.session:
			session = item.session
			btncls = ""
			timecls = " text-danger"
			room = session.room
			building = session.building+"."
			if dispatched:
				itime = time-dispatched
				longtime = dispatched
		else:
			session = None
			building = ""
			btncls = " disabled"
			if item.away:
				room = "Away"
				timecls = " text-warning"
				if dispatched:
					itime = time-dispatched
					longtime = dispatched
			else:
				room = "-"
				timecls = " text-success"
				if returned:
					itime = time-returned
					longtime = returned
					
		rowstyle = "row-even" if count % 2 == 0 else "row-odd"
		
	%>
		<tr class="${rowstyle}">
			<td><a href="${uurl}" class="linkcell${timecls}">${item.firstname}</a></td>
			<td><a href="${uurl}" class="linkcell${timecls}">${item.lastname}</a></td>
			<td><a href="${uurl}" class="linkcell">${item.phone}</a></td>
% if longtime:
			<td><a href="${uurl}" class="linkcell${timecls}"><abbr title="${strftime(TIMEFORMAT, localtime(longtime))}">${distance_of_time_in_words(itime)}</abbr></a></td>
% else:
			<td><a href="${uurl}" class="linkcell${timecls}">?</abbr></a></td>
% endif
% if room and len(room) < 16:
			<td><a href="${uurl}" class="linkcell"><strong>${building}</strong>${room}</a></td>
% elif room:
			<td><a href="${uurl}" class="linkcell"><strong>${building}</strong><abbr title="${room}">${room[:15]+u"\u2026"}</abbr></a></td>
% else:
			<td><a href="${uurl}" class="linkcell">-</a></td>
% endif
			<td><a href="${uurl}" class="linkcell">${item.comment}</a></td>
			<td><a href="${request.route_url("admin_helper_returned_list", id=item.id)}" class="btn btn-primary btn-xs${btncls}">${"Returned" if not session else "Return"}</a></td>
		</tr>
	<%	count += 1 %>
% endfor
	</table>
	</div>
</div>