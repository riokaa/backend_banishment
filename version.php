<?php
	require 'config/DBConfig.php';
    header('Content-Type:application/json');
    $db = new DBConfig();
    try {
	    $conn = new PDO("mysql:host=" . $db->get('host') . ";dbname=" . $db->get('sheet'), $db->get('username'), $db->get('password'));
	    $conn -> setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
	    $conn->exec("SET NAMES utf8");
    } catch(PDOException $e) {
    	echo "conn_error:<br/>" . $e -> getMessage();
    }
    $sql_version = "select * from version where id=(select max(id) from version wherer environment='pro');";
    $result = $conn->query($sql_version)->fetchAll(PDO::FETCH_ASSOC);
    $json['status'] = count($result);
    $json['info'] = $result;

    echo json_encode($json,JSON_UNESCAPED_UNICODE);
 ?>