// Establish socketIO connection
var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', function(){
  console.log('Websocket connected on table_test!');
});      

var noEntries = true;
var table;
// Datatables
$(document).ready(function() {
  table = $('#sqlTable').DataTable();
} );

socket.on('update table', function(jsonData){
  /** Calls function that updates and redraws table.
   */
  console.log("recieved update table on visualization");
  updateTable(jsonData); //update table with json from the database
  // data.sort([{column: 2}, {column: 1}]);
});

function updateTable(jsonData) {
  /** Updates table with new values. If a sensor doesn't exist, create new row and populate it.
   *   var jsonData = ["testName", "testValue", "2000-01-01 00:00:01"]
  */
  console.log("RUNNING UPDATE TABLE");
  // console.log("jsonData: " + jsonData);
  var parsedData = JSON.parse(jsonData);
  // console.log(parsedData);
  // Id of the sensor
  var id = parsedData[0];
  // console.log("id: " + id);
  var value = parsedData[1];
  var timestamp = parsedData[2];

  //sort data according to column 1 in ascending order
  // data.sort({column: 0});
  table.order( [[ 0, 'asc' ]] );
  // Gets exisiting ids of sensors in the tables
  var existing_ids = get_existing_ids(); // Type: Object array in ascending order
  console.log("existing ids: " + existing_ids);
  // console.log("existing ids type: " + typeof(existing_ids));
// test
  console.log('0,0 table cell' + table.cell(0,0).data())


  if (noEntries == true){
    // data.addRow(parsedData);
    table.row.add(parsedData).draw(false);
    console.log("creating new row from noEntries")
    noEntries = false;
    existing_ids = get_existing_ids();// Update existing id to new value
  }

  if (existing_ids.includes(id)){
    i = existing_ids.indexOf(id)
    console.log("i: " + existing_ids[i]);
    console.log('updating old row');
    table.row(i).data(parsedData).draw(false);
  }
  else {
    console.log('creating new row');
    // Create a new row and populate
    table.row.add(parsedData).draw(false);
  }
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

function get_existing_ids(){
  var existing_ids = []
  var i;
  for (i = 0; i < table.data().count(); i++) {
    // table.cell(row, column)
    cell_id = table.cell(i,0).data();
    existing_ids.push(cell_id);

  return existing_ids
}
}
