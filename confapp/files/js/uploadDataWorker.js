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

var token = "";

importScripts('/files/js/papaparse.min.js')

onmessage = function(e) {
    const data = e.data;
    const type = data.type;
    const arg = data.arg;
    // console.log('Message received from main script');
    switch (type) {
      case 'getValues':
        getValues(arg[0], arg[1], arg[2]) //f, columnnum, nameid
        break;
      case 'getHeaders':
        getHeaders(arg[0]) //f
        break;
      default:
        console.error('invalid type passed in');
        break;
    }
}

function getValues(f, column, nameid) {
  const possibleoptions = new Set();
  var doneheader = false;
  Papa.parse(f, {
    "header": false,
    "step": function(r,p) {
      if (doneheader == true) { return; }
      doneheader = true;
      var opt = r["data"][column].trim();
      if (opt) {
        possibleoptions.add(opt);
      }
    },
    "complete": function(r,p) {
      postMessage({type: "gotValues", data: [possibleoptions, nameid]});
    },
    "skipEmptyLines": true,
    "fastMode": false,
  });
}

function getHeaders(f) {
  var rows = 0;
  Papa.parse(f, {
    "header": false,
    "step": function(r,p) {
      var headers = []
      for (const h of r["data"]) {
        headers.push(h)
      }
      sendHeaders(rows, headers);
      p.abort();
    },
    "complete": function(r,p) {},
    "skipEmptyLines": true,
    "fastMode": false,
  });
}
function sendHeaders(rows, headers) {
  postMessage({
    type: "getHeaders",
    data: headers,
  });
}

function mergelog(s) {
  postMessage({
    type: "mergelog",
    data: s,
  });
}
