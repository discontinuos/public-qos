<?php
$rootPath = dirname(__FILE__);

date_default_timezone_set('UTC');

function errHandle($errNo, $errStr, $errFile, $errLine) {
    $msg = "$errStr in $errFile on line $errLine";
    if ($errNo == E_NOTICE || $errNo == E_WARNING) {
        throw new ErrorException($msg, $errNo);
    } else {
        echo $msg;
    }
}
set_error_handler('errHandle');

$rootPath = dirname(__FILE__);
require_once $rootPath . '/params.php';
require_once $rootPath . '/reader.php';
require_once $rootPath . '/cache.php';
require_once $rootPath . '/table.php';

function StartHtml()
{
?>
<html>
<title>Dumb-viewer</title>
<style>
td {
    font-size: 13px;
}
h4 {
    margin-bottom: 6px;
    margin-top: 12px;
}</style>
<body style='font-family: arial; font-size: 16px'>
<?php
}

function StartsWith($haystack, $needle)
	{
		return !strncmp($haystack, $needle, strlen($needle));
	}
