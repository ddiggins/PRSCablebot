/* Setup Socket.io Connector */
// Sending a connect request to the server.
var socket = io.connect('http://' + document.domain + ':' + location.port);
// Verify that connection has been established
socket.on('connect', function(){
    console.log('Websocket connected!');
});      

function update_power_slider() {
    /* Update slider value */
    let slider = document.getElementById("motorPower");
    let display = document.getElementById("displayPower");
    display.innerHTML = slider.value;
}

function update_speed_slider() {
    /* Update slider value */
    let slider = document.getElementById("encoderSpeed");
    let display = document.getElementById("displaySpeed");
    display.innerHTML = slider.value;
}

function send_motor_power() {
    /*  Send motor power to to app.py via socket.io,
        called by changing power slider value */
    var slider = document.getElementById("motorPower");
    console.log('Sending motor power!');
    socket.emit('new motor power', slider.value);
    $("#outgoing").load(location.href + " #outgoing");
}

function send_encoder_speed() {
    /*  Send encoder speed to app.py via socket.io,
        called by changing speed slider value */
    var slider = document.getElementById("encoderSpeed");
    console.log('Sending encoder speed!');
    socket.emit('new motor target', slider.value);
    $("#outgoing").load(location.href + " #outgoing");
}

function send_encoder_position() {
    /*  Send encoder position to app.py via socket.io,
        called by changing position slider value */
    var input = document.getElementById("encoderPosition");
    position = input.value*2887 //Converting meters to encoder steps
    console.log('Sending encoder position!');
    socket.emit('new motor target', position);
    input.value=''; // Resetting input field to zero
    $("#outgoing").load(location.href + " #outgoing");
}

function send_serial_command(){
    /*  Send serial command to app.py via socket.io,
        called by submitted a command in the "Manual" tab in Robot Controls */
    var input = document.getElementById("serialSend");
    command = input.value
    console.log('command type' + typeof(command))
    console.log('Sending serial command!');
    socket.emit('send serial command', command);
    input.value=''; // Resetting input field to zero
    $("#outgoing").load(location.href + " #outgoing");
}

function toggle_motor(){
    // Enable/Disable Motor and update appearance of motorStatus buttons 
    // There are multiple motorStatus buttons because there is one nested in each tab
    console.log('inside toggle motor')
    var elem = document.getElementById("motorStatus1");
    if (elem.value=="Enable Motor"){
        console.log("emit enable motor")
        socket.emit('enable motor');
        elem.value = "Disable Motor";
        document.getElementById("motorStatus2").value = "Disable Motor";
        document.getElementById("motorStatus3").value = "Disable Motor";
        document.getElementById("motorStatus4").value = "Disable Motor";
    }
    else{
        socket.emit('disable motor');
        elem.value = "Enable Motor";
        document.getElementById("motorStatus2").value = "Enable Motor";
        document.getElementById("motorStatus3").value = "Enable Motor";
        document.getElementById("motorStatus4").value = "Enable Motor";
    } 
    $("#outgoing").load(location.href + " #outgoing");
}

// Toggle Power
$("#v-pills-power-tab").on('show.bs.tab', function() {
    console.log('toggle motor from tab');
    socket.emit('new motor mode', "0");
});

// Toggle Speed
$("#v-pills-speed-tab").on('show.bs.tab', function() {
    console.log('toggle speed from tab');
    socket.emit('new motor mode', "2");
});

// Toggle Position
$("#v-pills-position-tab").on('show.bs.tab', function() {
    console.log('toggle position from tab');
    socket.emit('new motor mode', "1");
    $("#outgoing").load(location.href + " #outgoing");
});
