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
		timecls = "text-success"
		dispatched = item.dispatched
		returned = item.returned
		longtime = None
		itime = None
		if item.session:
			session = item.session
			btncls = ""
			timecls = "text-danger"
			loc = session.location
			if dispatched:
				itime = time-dispatched
				longtime = dispatched
		else:
			session = None
			btncls = " disabled"
			if item.away:
				loc = "Away"
				timecls = "text-danger"
				if dispatched:
					itime = time-dispatched
					longtime = dispatched
			else:
				loc = "-"
				timecls = "text-success"
				if returned:
					itime = time-returned
					longtime = returned
					
		userstyle = "user usereven" if count % 2 == 0 else "user userodd"
		
	%>
		<tr>
			<td class="${userstyle}"><a href="${uurl}" class="linkcell"><abbr title="${item.phone}">${item.firstname}.${item.lastname[:1]}</abbr></a></td>
% if longtime:
			<td class="${userstyle}"><a href="${uurl}" class="linkcell ${timecls}"><abbr title="${strftime(TIMEFORMAT, localtime(longtime))}">${distance_of_time_in_words(itime)}</abbr></a></td>
% else:
			<td class="${userstyle}"><a href="${uurl}" class="linkcell ${timecls}">?</abbr></a></td>
% endif
			<td class="${userstyle}"><a href="${uurl}" class="linkcell"><abbr title="${loc}">${loc[:4]}</a></td>
			<td class="${userstyle}"><a href="#" onclick='helper_returned("${request.route_url("admin_helper_returned", id=item.id)}");return false;' class="btn btn-primary btn-xs${btncls}">${"Ret" if not session else "Ret'd"}</a></td>
		</tr>
	<%	count += 1 %>
% endfor
