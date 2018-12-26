<?php

class cache
{
	private $rootPath = "";

	public function cache($rootPath)
	{
		$this->rootPath = $rootPath;
		$this->folder = $rootPath . "/cache";
		if (!is_dir($this->folder))
			mkdir($this->folder);
	}

	function resolveFile($params)
	{
		$key = $params->currentLinkArgs(false);
		return $this->folder . "/" . $key . ".dat";
	}
	public function hasData($params)
	{
		$cacheFile = $this->resolveFile($params);
		$file =  $params->curDatasetFilename;
		$ret = file_exists($cacheFile) &&
			filemtime($file) == filemtime($cacheFile);
		return $ret;
	}
	public function read($params)
	{
		$cacheFile = $this->resolveFile($params);
		return self::ReadData($cacheFile);
	}
	public function keep($params, $table)
	{
		$cacheFile = $this->resolveFile($params);
		$file = $params->curDatasetFilename;
		
		self::WriteData($cacheFile, $table);
		
		$time = filemtime($file);
		touch($cacheFile, $time, time());
	}
	
	public static function ReadAllText($path, $maxLength = -1)
	{
		if ($maxLength == -1)
			return file_get_contents($path);
		else
			return file_get_contents($path, false, NULL, -1, $maxLength);
	}
	public static function WriteAllText($path, $text)
	{
		return file_put_contents($path, $text);
	}
	public static function WriteData($path, $text)
	{
		return self::WriteAllText($path, serialize($text));
	}
	public static function ReadData($path)
	{
		$text = self::ReadAllText($path);
		return unserialize($text);
	}
}
