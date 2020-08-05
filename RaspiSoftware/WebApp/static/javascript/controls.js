/* Setup Socket.io Connector */
// Sending a connect request to the server.
var socket = io.connect('http://' + document.domain + ':' + location.port);
// Verify that connection has been established
socket.on('connect', function(){
    console.log('Websocket connected!');
});      

socket.on('testing deployment socket', function(){
    console.log('getting message from deployment')
});

var update_power_slider = function() {
    /* Update slider value */
    let slider = document.getElementById("motorPower");
    let display = document.getElementById("displayPower");
    display.innerHTML = slider.value;
}

var update_speed_slider = function() {
    /* Update slider value */
    let slider = document.getElementById("encoderSpeed");
    let display = document.getElementById("displaySpeed");
    display.innerHTML = slider.value;
}

var send_motor_power = function() {
    /*  send motor power to python via Websockets
        called by changing slider value */
    var slider = document.getElementById("motorPower");
    console.log('Sending motor power!');
    socket.emit('new motor power', slider.value);
    $("#outgoing").load(location.href + " #outgoing");
}

var send_encoder_speed = function() {
    /*  send encoder speed to python via Websockets
        called by changing slider value */
    var slider = document.getElementById("encoderSpeed");
    console.log('Sending encoder speed!');
    socket.emit('new motor target', slider.value);
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

var toggle_power = function(){
    /*  turn on power mode */
    var power = document.getElementById("powerStatus");
    var speed = document.getElementById("speedStatus");
    var position = document.getElementById("positionStatus");
    if (power.value=="Power Disabled"){
        socket.emit('new motor mode', "0");
        power.value = "Power Enabled";
        speed.value = "Speed Disabled";
        position.value = "Position Disabled";
    }
    $("#outgoing").load(location.href + " #outgoing");
}

var toggle_speed = function(){
    /*  turn on speed mode */
    var power = document.getElementById("powerStatus");
    var speed = document.getElementById("speedStatus");
    var position = document.getElementById("positionStatus");
    if (speed.value=="Speed Disabled"){
        socket.emit('new motor mode', "2");
        power.value = "Power Disabled";
        speed.value = "Speed Enabled";
        position.value = "Position Disabled";
    }
    $("#outgoing").load(location.href + " #outgoing");
}

var toggle_position = function(){
    /*  turn on position mode */
    var power = document.getElementById("powerStatus");
    var speed = document.getElementById("speedStatus");
    var position = document.getElementById("positionStatus");
    if (position.value=="Position Disabled"){
        socket.emit('new motor mode', "1");
        power.value = "Power Disabled";
        speed.value = "Speed Disabled";
        position.value = "Position Enabled";
    }
    $("#outgoing").load(location.href + " #outgoing");
}

// upload file
// $(function() {
//     $('#uploadFileButton').click(function() {
//         var form_data = new FormData($('#upload')[0]);
//         $.ajax({
//             type: 'POST',
//             url: '/',
//             data: form_data,
//             contentType: false,
//             cache: false,
//             processData: false,
//             async: false,
//             success: function(data) {
//                 console.log('Successfully uploaded file!');
//             },
//         });
//     });
// });
