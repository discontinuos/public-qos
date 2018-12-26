<?php 

// Configuración
$key = 'xds5434345454ds';
$expandFiles = false;
$dataFolder = "storage/monitors";


// Listo 
$rootPath = dirname(__FILE__);
$path = $rootPath  . "/" . $dataFolder;

if (array_key_exists("key", $_POST))
{
	if ($key != $_POST['key'])
	{
		echo 'Mismatch key.';
		exit();
	}
	$command = $_POST['command'];
	switch($command)
	{
		case "put":
			$filename = $_POST['filename'];
			$instance = $_POST['instanceId'];
			if (EndsWith($filename, ".zip") == false || Contains($filename, "/") || Contains($filename, "\\"))
			{
				echo 'Invalid filename.';
				exit();
			}
			if (Contains($instance, "/") || Contains($instance, "\\"))
			{
				echo 'Invalid instance name.';
				exit();
			}
			$instancePath = $path . "/" . $instance;
			EnsureExists($instancePath);
			$fullFilename = $instancePath . "/" . $filename;
			move_uploaded_file($_FILES['file']['tmp_name'], $fullFilename);
	
			if ($expandFiles)
			{
				$zip = new ZipArchive();
				if ($zip->open($fullFilename) === TRUE)
				{
					$zip->extractTo($instancePath);
					$zip->close();
				} else {
					echo 'Failed.';
				}
			}
			echo 'OK';
			break;
		default:
			echo 'Unrecognized command.';
	}
	exit();
}
	
	function EndsWith($haystack, $needle)
	{
		$length = strlen($needle);
		if ($length == 0)
			return true;
		return (substr($haystack, -$length) === $needle);
	}
	function Contains($haystack, $needle)
	{
		$pos = strpos($haystack , $needle);
		if ($pos === false)
			return false;
		else
			return true;
	}
	function EnsureExists($directory)
	{
		if (!is_dir($directory))
		{
			EnsureExists(dirname($directory));
			mkdir($directory);
		}
	}
?>
<form enctype="multipart/form-data"	method=post>
Command: <input type=text name=command value='put' /><p>
Key: <input type='text' name='key' /><p>
Filename (month.zip): <input type='text' name='filename' /><p>
InstanceId: <input type='text' name='instanceId' /><p>
File: <input type='file' name='file' /><p>
<input type='submit' value='submit' />
</form>