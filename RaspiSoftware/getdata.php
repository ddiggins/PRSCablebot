<?php

$host="localhost";
$user="databaseUser",
$password="user",
$database=database_name

$con = mysqli_connect("localhost","databaseUser","user", "");
if (!$con) {
  die(‘Could not connect: ‘ . mysqli_error($con));
}

$qry = "SELECT topping, slices FROM `pizza`"

$result = mysqli_query($con,$qry);
mysqli_close($con);

?>