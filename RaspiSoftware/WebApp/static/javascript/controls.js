/* Setup Socket.io Connector */
// Sending a connect request to the server.
var socket = io.connect('http://' + document.domain + ':' + location.port);
// Verify that connection has been established
socket.on('connect', function(){
    console.log('Websocket connected!');
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
