/* Setup Socket.io Connector */
// Sending a connect request to the server.
var socket = io.connect('http://' + document.domain + ':' + location.port);
// Verify that connection has been established
socket.on('connect', function(){
    console.log('Websocket connected!');
});
              
socket.on('update table', function(data){
/*  Update incoming/outgoing display 
 on command from Websockets*/
var message = JSON.parse(data);
console.log("incoming message:", data.toString());
console.log("id: ", message.id.toString());

// Refreshes the incoming section of the webpage.
document.getElementById("incoming").innerHTML = data.toString();

//Adds section to table
var table = document.getElementById("statusTable");
var row = table.insertRow(-1); //Inserts row at the bottom of the table
var cell1 = row.insertCell(0);
var cell2 = row.insertCell(1);
cell1.innerHTML = message.id.toString();
cell2.innerHTML = data.toString();

var i = 0;

$("#statusTable tr").each(function() {
    var val1 = $(table.rows[i].cells[0]).text();
    i++;
});


    $("tr.item").each(function() {
        var quantity1 = $(this).find("input.name").val(),
            quantity2 = $(this).find("input.id").val();
    });
});          

var updateSlider = function() {
    /* Update slider value */
    let slider = document.getElementById("motorSpeed");
    let display = document.getElementById("display");
    display.innerHTML = slider.value;
}

var send_motor_speed = function() {
    /*  send motor speed to python via Websockets
        called by changing slider value */
    var slider = document.getElementById("motorSpeed");
    console.log('Sending motor speed!');
    socket.emit('new motor speed', slider.value);
    $("#outgoing").load(location.href + " #outgoing");
}

var toggle_motor = function(){
    /*  send enable or disable command to flask */
    var elem = document.getElementById("motorStatus");
    if (elem.value=="Enable Motor"){
        socket.emit('enable motor');
        elem.value = "Disable Motor";
    }
    else{
        socket.emit('disable motor');
        elem.value = "Enable Motor";
    } 
    $("#outgoing").load(location.href + " #outgoing");
}
