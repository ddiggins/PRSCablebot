// Establish socketIO connection
var socket = io.connect('http://' + document.domain + ':' + location.port);

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

socket.on('update table', function(jsonData){
  /** Calls function that updates and redraws table.
   */
  console.log("recieved update table on visualization");
  updateTable(jsonData); //update table with json from the database
  drawTable();
});

function updateTable(jsonData) {
  /** Updates table with new values. If a sensor doesn't exist, create new row and populate it.
   *   var jsonData = ["testName", "testValue", "2000-01-01 00:00:01"]
  */
  console.log("RUNNING UPDATE TABLE");
  console.log("jsonData: " + jsonData);
  var parsedData = JSON.parse(jsonData);
  console.log(parsedData)
  // Id of the sensor
  var id = parsedData[0]
  console.log("id: " + id)
  var value = parsedData[1]
  var timestamp = parsedData[2]
  // Gets exisiting ids of sensors in the tables
  var existing_ids = data.getDistinctValues(0) // Type: Object array
  console.log("existing ids: " + existing_ids)

  // Check whether sensor already exists in the table.
  for (i = 0; i < existing_ids.length; i++) {
    // If row with matching sensor name exists, updates existing row
    if (id == existing_ids[i]){
      console.log("i: " + existing_ids[i]);
      data.setCell(i, 1, value);  // setCell(row, column)
      data.setCell(i, 2, timestamp);
    }
    else{
      // Create a new row and populate
      data.addRow(parsedData);
    }
  }
};


function drawTable(){
  table.draw(data, {showRowNumber: true, width: '100%', height: '100%'});
};
