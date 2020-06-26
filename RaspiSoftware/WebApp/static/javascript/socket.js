// $(document).ready(function(){
//     //Sending a connect request to the server.
//     var socket = io.connect('http://' + document.domain + ':' + location.port);
//     //Verify that connection has been established
//     socket.on('connect', function(){
//         console.log('Websocket connected!');
//     });
    
//     // Listens to "new incoming" message and updates incoming value.
//     socket.on('new incoming', function(data){
//         console.log("incoming message:", data.toString())
//         document.getElementById("incoming").innerHTML = data.toString();

//     });
// });

var slider = document.getElementById("motorSpeed");
var output = document.getElementById("display");
output.innerHTML = slider.value; // Display the default slider value

// Update the current slider value (each time you drag the slider handle)
slider.oninput = function() {
    output.innerHTML = this.value;
}


 

function send_motor_speed(){
    var slider = document.getElementById("motorSpeed");
    // var motor_speed = {speed : slider.value};
    console.log('Sending motor speed!');
    socket.emit('new motor speed', slider.value);
    $("#outgoing").load(location.href + " #outgoing");
}

function toggle_motor(){
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

socket.on('update', function(data){
    console.log("incoming message:", data.toString())
    document.getElementById("incoming").innerHTML = data.toString();
}); 
