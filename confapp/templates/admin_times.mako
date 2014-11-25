<%inherit file="admin-base.mako"/>
<% from time import localtime, strftime 
from confapp.libs.helpers import distance_of_time_in_words
TIMEFORMAT = "%H:%M:%S"
%>
<div class="container">
	<div class="row">
		<div class="col-xs-9">
			<h2>${section} list</h2>
		</div>
	</div>
	<div class="row">
	<table class="table col-xs-12">
		<thead class="table-header">
			<tr>
				<th> Building </th>
				<th> Time took (avg.) </th>
			</tr>
		</thead>
<% count = 0 %>
% for item in items:
	<%	
		userstyle = "user usereven" if count % 2 == 0 else "user userodd"
	%>
		<tr>
			<td class="${userstyle}">${item[0]}</td>
			<td class="${userstyle}">${distance_of_time_in_words(item[1])}</td>
		</tr>
	<%	count += 1 %>
% endfor
	</table>
	</div>
</div>