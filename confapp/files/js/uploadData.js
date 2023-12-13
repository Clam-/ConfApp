if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) {
      return typeof args[number] != 'undefined'
        ? args[number]
        : match
      ;
    });
  };
}

var myWorker = new Worker('/files/js/uploadDataWorker.js');

function mergelog(s) {
  console.log(s);
}

const workerMaker = (type, arg) => {
  // check if a worker has been imported
  if (window.Worker) {
    myWorker.postMessage({type, arg});
  }
}

myWorker.onmessage = function(ev) {
  //console.log('Message received from worker');
  const response = ev.data;
  const data = response.data;
  const type = response.type;
  if (type === 'mergelog') { mergelog(data); }
  else if( type === 'getHeaders') { handleFilesDone(data); }
  else if( type === 'gotValues') { gotValues(data); }
  else if ( type == 'changedBuilding') { changedBuilding(data); }
  else { console.error('An Invalid type has been passed in'); }
}
CSVFILE = null;

function autoSelectRules(data) {
  data = data.toLowerCase();
  if (data.includes("school") || data.includes("college") || data.includes("grammar") ) { return true; }
  else if (data.endsWith(" ps")) { return true; }
  return false;
}

function getValues(nameid) {
  return (event) => {
    workerMaker('getValues', [CSVFILE, event.target.value, nameid]);
  }
}
function gotValues(data) {
  //data is actually a Set and nameid list :
  var options = data[0];
  var nameid = data[1]
  var listelem = jQuery("#csvfields2");
  for (var i of nameid) {
    // delete select if exists
    listelem.children("li").children("select#"+i[1])
    // create select list item
    var s = jQuery("<select id='{0}' name='{0}' multiple></select>".format(i[1]));
    s.append(jQuery("<option></option>").attr("value", "").text("(NONE)"));
    for (const opt of options) {
      if ((i[1] == "shirtopts" && autoSelectRules(opt)) ||
          (i[1] == "sports" && opt == "SP"))  {
        // lol auto select anything with "school", "college",
        // also auto select sports building
        s.append(jQuery("<option></option>").attr("value", opt).attr("selected","selected").text(opt));
      } else { s.append(jQuery("<option></option>").attr("value", opt).text(opt)); }
    }
    listelem.append(jQuery("<li></li>").append(jQuery("<span>{0}</span>".format(i[0])).add(s)));
  }
}

function handleFiles(flist) {
  // clear csvfields
  jQuery('#csvfields li').remove();
  jQuery('#csvfields2 li').remove();
  // getHeaders
  CSVFILE = flist[0]
  workerMaker('getHeaders', [CSVFILE]);
}

function handleFilesDone(data) {
  // DEPENDING ON WHAT UPLOAD TYPE, generate fields...
  var type = document.getElementById("utype").value;
  var fields = [];
  if (type == "sessionlocs") {
    fields = [["Code:", "code"], ["Building No.:", "buildnum"], ["Building Name:", "buildname"],
      ["Room:", "room"], ["Title:", "title"],
      ["Session Type:", "sessiontype"], ["Number of registered", "numreg"], ["Capacity", "capacity"]]
  } else if (type == "people") {
    fields = [["Code:", "sessioncode"], ["First Name:", "firstname"], ["Last Name:", "lastname"], ["Reg ID:", "regid"],
      ["Email:", "email"], ["Phone:", "phone"], ["Organisation:", "org"], ["Shirt Qualifier", "shirt"],
      ["What is a presenter?:", "presqual"]]
  } else if (type == "hosts") {
    fields = [["Code:", "sessioncode"], ["First Name:", "firstname"], ["Last Name:", "lastname"], ["Phone:", "phone"]
      , ["Email:", "email"]]
  } else if (type == "cancelled") {
    fields = [["Code:", "code"], ["Building No.:", "buildnum"], ["Building Name:", "buildname"], ["Venue:", "room"]]
  } else if (type == "sessioncaps") {
    fields = [["Title:", "title"], ["Numbers:", "numbers"]]
  }
  var headers = data;
  jQuery('#csvfields li').remove();
  jQuery('#csvfields2 li').remove();
  var listelem = jQuery("#csvfields");
  for (var i of fields) {
    // create select list item
    var s = null;
    if (["sessioncode", "phone", "presqual"].includes(i[1])) { s = jQuery("<select id='{0}'  name='{0}' multiple></select>".format(i[1])); }
    else { s = jQuery("<select id='{0}' name='{0}'></select>".format(i[1])); }
    s.append(jQuery("<option></option>").attr("value", "").text("(NONE)"));
    for (const [index, h] of headers.entries()) {
      s.append(jQuery("<option></option>").attr("value", index).text(h));
    }
    if (i[1] == "buildnum") { s.change(getValues([["Sports Building(s):", "sports"]])); }
    else if (i[1] == "shirt") { s.change(getValues([["Valid shirt options:", "shirtopts"]])); }
    else if (i[1] == "presqual") { s.change(getValues([["Valid presenter options:", "presopts"]])); }

    listelem.append(jQuery("<li></li>").append(jQuery("<span>{0}</span>".format(i[0])).add(s)));
  }
}

window.addEventListener("load", _ => {
});
