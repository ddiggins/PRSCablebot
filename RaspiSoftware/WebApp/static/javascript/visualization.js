// Establish socketIO connection
var socket = io.connect('http://' + document.domain + ':' + location.port);


// Google charts set up
google.charts.load('current', {'packages':['table']});
// Set a callback to run when the Google Visualization API is loaded.
google.charts.setOnLoadCallback(drawTable);

function drawTable() {
    var jsonData =    [1, "2000-01-01 00:00:01", "testName", "testValue"]

    
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Sensor Name');
    data.addColumn('string', 'Time Stamp'); //Is actually a sql timestamp object, but can turn into a string
    data.addColumn('string', 'Value');
    data.addRows([
      ['Mike',  {v: 10000, f: '$10,000'}, true],
      ['Jim',   {v:8000,   f: '$8,000'},  false],
      ['Alice', {v: 12500, f: '$12,500'}, true],
      ['Bob',   {v: 7000,  f: '$7,000'},  true]
    ]);
    data.addRows(jsonData);

    var table = new google.visualization.Table(document.getElementById('sqlTable'));

    table.draw(data, {showRowNumber: true, width: '100%', height: '100%'});
  }
