<%inherit file="admin-special-base.mako"/>
<div class="maxbig">
	<h2>Registrations for ${section.description}</h2>
	<table class="table">
		<thead class="table-header">
			<tr>
				<th> Reg&rsquo;d </th>
				<th> Last name </th>
				<th> First name </th>
				<th> Type </th>
				<th class="spacer"></th>
				<th> Code </th>
				<th> Session title </th>
				<th> Evaluations </th>
				<th> Comment </th>
			</tr>
		</thead>
<% 
count = 0 
items = page.items
%>

% for item in items:
	<%	
		session = item.session
		person = item.person
		
		sessionstyle = "session sessioneven" if count % 2 == 0 else "session sessionodd"
		
		if session.equipment == session.equip_returned:
			cellstyle = sessionstyle
		else:
			cellstyle = "table-cell-bad-even" if count % 2 == 0 else "table-cell-bad-odd"
		
		uurl = request.route_url("admin_day_edit", day=section.description, session=session.id, person=person.id)
	%>
		<tr>
			<td class="table-cell-reg ${sessionstyle}">${u"\u2714" if item.registered else ""}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${person.lastname}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${person.firstname}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${item.type}</a></td>
			
			<td class="spacer"></td>
			
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${session.code}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${session.title[:25]}&hellip;</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${session.evaluations}</a></td>
			<td class="${sessionstyle}"><a href="${uurl}" class="linkcell">${session.comments}</a></td>
		</tr>
	<%	count += 1 %>
% endfor
	</table>
	<p>Page: ${page.pager()}</p>
</div>