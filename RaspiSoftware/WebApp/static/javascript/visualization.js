// Establish socketIO connection
var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function(){
    console.log('Websocket connected on table_test!');
});      

// Set to false once the first row has been made in a table
var logsNoEntries = true;
var dataNoEntries = true

// Initializes Datatables
var robotLogsTable;
var aquatrollDataTable;
$(document).ready(function() {
    robotLogsTable = $('#robotLogsTable').DataTable({
        "searching": false,
        "lengthMenu": [[5, 10, 25, 50, -1], [5, 10, 25, 50, "All"]]
    });
    aquatrollDataTable = $('#aquatrollDataTable').DataTable({
        "lengthMenu": [[5, 10, 25, 50, -1], [5, 10, 25, 50, "All"]]
    });
} );

socket.on('update robot logs table', function(jsonData){
    // console.log("recieved update ROBOT table");
    logsNoEntries = updateTable(jsonData, robotLogsTable, logsNoEntries); //update table with json from the database
});

socket.on('update Aqua TROLL data table', function(jsonData){
    // console.log("recieved update DATA table");
    dataNoEntries = updateTable(jsonData, aquatrollDataTable, dataNoEntries);
  });

function updateTable(jsonData, table, noEntries) {
    /*
    Updates table with new values. If a sensor doesn't exist, create new row and populate it.
    var jsonData = ["testName", "testValue", "2000-01-01 00:00:01"]
    Parameters:
        jsonData - data to be put into the table
        table - table to be updated
        noEntries - boolean checking whether there are any existing rows in the table
    Returns:
        noEntries - if noEntries was set to false locally, returns boolean so that the global variable
                    can be updated.
    */ 
    // console.log("RUNNING UPDATE TABLE");
    var parsedData = JSON.parse(jsonData);
    var id = parsedData[0];
    // Sort data according to the first column in ascending order
    // table.order( [[ 0, 'asc' ]] );
    // Gets exisiting ids of sensors in the tables
    var existing_ids = get_existing_ids(table); // Type: List of ids in table already
    // console.log("existing ids: " + existing_ids);

    if (noEntries == true){
        // If the table is empty, create the first row
        table.row.add(parsedData).draw(false);
        console.log("creating new row from noEntries")
        noEntries = false;
        existing_ids = get_existing_ids(table);// Update existing id to new value
    }

    if (existing_ids.includes(id)){
        // If the table already has a row of that sensor, update data and redrew
        // console.log('updating old row');
        i = existing_ids.indexOf(id);
        table.row(i).data(parsedData).draw(false);
    }
    else {
        // Create a new row
        // console.log('creating new row');
        table.row.add(parsedData).draw(false);
    }
    return noEntries
};

function get_existing_ids(table){
    var existing_ids = [];
    var i;
    for (i = 0; i < table.data().count(); i++) {
        cell_id = table.cell(i,0).data();
        existing_ids.push(cell_id);
    }
    return existing_ids;
}

// Update progress bar
socket.on('update progress bar', function(progressVal){
    console.log("updating progress bar");
    // console.log('progress val:' + progressVal);
    var progressBar = document.getElementById("deploymentProgress");  
    document.getElementsByClassName('progress-bar').item(0).setAttribute('aria-valuenow',progressVal);
    document.getElementsByClassName('progress-bar').item(0).setAttribute('style','width:'+Number(progressVal)+'%');
});