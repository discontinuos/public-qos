<?php
$rootPath = dirname(__FILE__);
require_once $rootPath . '/initialize.php';

$params = new Params();
$params->resolveDateset($rootPath);
$params->resolveView();
$params->resolveMetric();

if ($params->SafeGetParam('download') == "1")
{
	$file = $params->curDatasetFilename;
	header("Content-Type: text/csv");
	$filter = $params->SafeGetParam('filter'); 
	if ($filter == "")
	{
		header("Content-Length: " . filesize($file));
		header("Content-Disposition: filename=\"" . $params->curDataset . "\"");
		readfile($file);
	}
	else
	{
		header("Content-Disposition: filename=\"" . $filter . "#" . $params->curDataset . "\"");
		$filter = str_replace('-', ';', $filter) . ";";
		$handle = fopen($file, "r");
		$line = fgets($handle);
		echo $line;
		while (($line = fgets($handle)) !== false) 
		{
			if (StartsWith($line, $filter))
				echo $line;
		}
    fclose($handle);
	}
	exit();
}

StartHtml();

$params->showDateset();
$params->showView();
$params->showMetric();

$cache = new cache($rootPath);
if ($cache->hasData($params) == false)
{
	$reader = new reader($rootPath);
	$table = $reader->read($params);
	$cache->keep($params, $table);
}
else
	$table = $cache->read($params);

$display = new table();
$display->show($params, $table);

$display->showdownload();
