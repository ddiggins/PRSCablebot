// Establish socketIO connection
var socket = io.connect('http://' + document.domain + ':' + location.port);

var clients = [];

// socket.on('connect', function(client){
//   console.log('Websocket connected on visualization!');
//   // console.log(' %s sockets connected on visualiztion', io.engine.clientsCount);
//   clients.push(client);

//   client.on('disconnect', function() {
//     console.log("disconnect: ", socket.id);
//     clients.splice(clients.indexOf(client), 1);
//   });
// });
socket.on('connect', function(){
  console.log('Websocket connected on visualization!');
});      


// Google charts set up
google.charts.load('current', {'packages':['table']});
// Set a callback to run when the Google Visualization API is loaded.
google.charts.setOnLoadCallback(initTable);
google.charts.setOnLoadCallback(drawTable);

var noEntries = true;

function initTable(){
  /** Sets DataTable and table global variables */
  data = new google.visualization.DataTable();
  data.addColumn('string', 'Sensor Name');
  data.addColumn('string', 'Value');
  data.addColumn('string', 'Time Stamp');

  table = new google.visualization.Table(document.getElementById('sqlTable'));
};

// Update progress bar
socket.on('update progress bar', function(progressVal){
  console.log("updating progress bar");
  console.log("progressvaltype:" + typeof progressVal)
  console.log('progress val:' + progressVal)
  var progressBar = document.getElementById("deploymentProgress");  
  document.getElementsByClassName('progress-bar').item(0).setAttribute('aria-valuenow',progressVal);
  document.getElementsByClassName('progress-bar').item(0).setAttribute('style','width:'+Number(progressVal)+'%');
});

socket.on('update table', function(jsonData){
  /** Calls function that updates and redraws table.
   */
  console.log("recieved update table on visualization");
  updateTable(jsonData); //update table with json from the database
  drawTable();
  data.sort([{column: 2}, {column: 1}]);
});

function updateTable(jsonData) {
  /** Updates table with new values. If a sensor doesn't exist, create new row and populate it.
   *   var jsonData = ["testName", "testValue", "2000-01-01 00:00:01"]
  */
  // console.log("RUNNING UPDATE TABLE");
  // console.log("jsonData: " + jsonData);
  var parsedData = JSON.parse(jsonData);
  // console.log(parsedData);
  // Id of the sensor
  var id = parsedData[0];
  // console.log("id: " + id);
  var value = parsedData[1];
  var timestamp = parsedData[2];

  //sort data according to column 1 in ascending order
  data.sort({column: 0});
  // Gets exisiting ids of sensors in the tables
  var existing_ids = data.getDistinctValues(0); // Type: Object array in ascending order
  // console.log("existing ids: " + existing_ids);

  if (noEntries == true){
    data.addRow(parsedData);
    // console.log("creating new row from noEntries")
    noEntries = false;
    existing_ids = data.getDistinctValues(0); // Update existing id to new value
  }

  // Check whether sensor already exists in the table.
  // for (i = 0; i < existing_ids.length; i++) {
  //   // If row with matching sensor name exists, updates existing row
  //   if (id == existing_ids[i]){
  //     console.log("i: " + existing_ids[i]);
  //     console.log('updating old row');
  //     data.setCell(i, 1, value);  // setCell(row, column)
  //     data.setCell(i, 2, timestamp);
  //   } else {
  //     console.log('creating new row');
  //     // Create a new row and populate
  //     data.addRow(parsedData);
  //   }
  // }

  if (existing_ids.includes(id)){
    i = existing_ids.indexOf(id)
    // console.log("i: " + existing_ids[i]);
    // console.log('updating old row');
    data.setCell(i, 1, value);  // setCell(row, column)
    data.setCell(i, 2, timestamp);
  }
  else {
    console.log('creating new row');
    // Create a new row and populate
    data.addRow(parsedData);
  }

};

var cssClassNames = {
  // headerRow: 'someclass',
  // tableRow: 'someclass',
  // oddTableRow: 'someclass',
  // selectedTableRow: 'someclass',
  // hoverTableRow: 'someclass',
  // headerCell: 'someclass',
  // tableCell: 'someclass',
  // rowNumberCell: 'someclass'
  headerRow: 'thead', 
}

function drawTable(){
  table.draw(data, {cssClassNames, showRowNumber: true, width: '100%', height: '100%', allowHtml: true});
  var className = 'google-visualization-table-table';
  $('.'+className).removeClass(className);
};


