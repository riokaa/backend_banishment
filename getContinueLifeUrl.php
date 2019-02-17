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
    $sql = "select value from information where type='continue_life_url' and value <> '' and value is not null limit 1;";
    $result = $conn->query($sql)->fetchAll(PDO::FETCH_ASSOC);
    if(count($result) > 0){
        $json['status'] = 1;
        $json['message'] = 'ok';
        $json['data'] = $result[0];
    }else{
        $json['status'] = 0;
        $json['message'] = 'error';
    }

    echo json_encode($json,JSON_UNESCAPED_UNICODE);
?>