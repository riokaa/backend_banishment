<?php
	require 'config/DBConfig.php';
	require 'config/Environment.php';

    header('Content-Type:application/json');
    $db = new DBConfig();
    $env = new Environment();
    try {
	    $conn = new PDO("mysql:host=" . $db->get('host') . ";dbname=" . $db->get('sheet'), $db->get('username'), $db->get('password'));
	    $conn -> setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
	    $conn->exec("SET NAMES utf8");
    } catch(PDOException $e) {
    	echo "conn_error:<br/>" . $e -> getMessage();
    }
    $sql = "select * from version where id=(select max(id) from version where environment='" . $env->getEnvironment() . "');";
    $result = $conn->query($sql)->fetchAll(PDO::FETCH_ASSOC);
    $json['status'] = count($result);
    if(count($result) == 1){
    	$json['info'] = $result[0];
    }

    echo json_encode($json,JSON_UNESCAPED_UNICODE);
 ?>