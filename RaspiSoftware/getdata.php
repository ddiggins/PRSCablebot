<?php

$con = mysqli_connect(‘localhost’,’root’,”,’master’);
if (!$con) {
  die(‘Could not connect: ‘ . mysqli_error($con));
}

$qry = "SELECT topping, slices FROM `pizza`"

$result = mysqli_query($con,$qry);
mysqli_close($con);

?>