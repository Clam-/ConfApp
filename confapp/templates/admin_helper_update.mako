<% from time import localtime, strftime 
from confapp.libs.helpers import distance_of_time_in_words
TIMEFORMAT = "%H:%M:%S"
%>
		<thead class="table-header">
			<tr>
				<th> Name </th>
				<th> Time </th>
				<th> Loc </th>
				<th> Ret </th>
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
		away = item.away
		if item.session:
			session = item.session
			btncls = ""
			timecls = " text-danger"
			loc = "%s.%s" % (session.building, session.room)
			if dispatched:
				itime = time-dispatched
				longtime = dispatched
		else:
			session = None
			btncls = " disabled"
			if away:
				loc = "Away"
				timecls = " text-warning"
				if dispatched:
					itime = time-dispatched
					longtime = dispatched
			else:
				loc = "-"
				timecls = " text-success"
				if returned:
					itime = time-returned
					longtime = returned
					
		rowstyle = "row-even" if count % 2 == 0 else "row-odd"
		comment = item.comment
	%>
		<tr class="${rowstyle}">
			<td><a href="${uurl}" class="linkcell${timecls}"><abbr title="${item.phone}">${item.firstname}.${item.lastname[:1]}</abbr></a></td>
% if longtime:
			<td><a href="${uurl}" class="linkcell${timecls}"><abbr title="${strftime(TIMEFORMAT, localtime(longtime))}">${distance_of_time_in_words(itime)}</abbr></a></td>
% else:
			<td><a href="${uurl}" class="linkcell${timecls}">?</abbr></a></td>
% endif
% if away and comment:
			<td><a href="${uurl}" class="linkcell"><abbr title="${item.comment}">${loc[:4]}</abbr></a></td>
% elif away:
			<td><a href="${uurl}" class="linkcell">${loc[:4]}</a></td>
% else:
			<td><a href="${uurl}" class="linkcell"><abbr title="${loc}">${loc[:4]}</abbr></a></td>
% endif
			<td><a href="#" onclick='helper_returned("${request.route_url("admin_helper_returned", id=item.id)}");return false;' class="btn btn-primary btn-xs${btncls}">${"Ret" if not session else "Ret'd"}</a></td>
		</tr>
	<%	count += 1 %>
% endfor
