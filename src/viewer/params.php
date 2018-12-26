<?php

class params
{
	public $datasets = null;
	public $curDataset = null;

	public $views = null;
	public $curView = null;

	public $metrics = null;
	public $curmetric = null;

	public $curDatasetFilename = null;

	public function resolveView()
	{
		$this->views = array('monthly' => 'Diario', 'hourly' => 'Horas', 'weekly' => 'Semanal');
		$curView = $this->SafeGetParam('view', 'monthly');

		if (array_key_exists($curView, $this->views) == false)
			$curView = $this->views[0];

		$this->curView = $curView; 
	}

	public function showView()
	{
		echo "<h4>Vista: &nbsp;&nbsp;&nbsp;" . $this->views[$this->curView] . "</h4>";
		echo "<small>Otras: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";

		foreach($this->views as $view => $label)
		{
			if ($this->curView  != $view)
				$this->showLink(
						$this->curDataset, $view,
						$this->curMetric, $this->views[$view]);				
		}
		echo "</small><br>";
	}

	public function getViewRange()
	{
		switch($this->curView)
		{
			case 'monthly':
				return '31';
			case 'hourly':
				return '23';
			case 'weekly':
				return '7';
			default:
				throw new exception('vista no reconocida');
		}
	}
	public function getViewRangeFrom()
	{
		switch($this->curView)
		{
			case 'monthly':
				return '1';
			case 'hourly':
				return '0';
			case 'weekly':
				return '1';
			default:
				throw new exception('vista no reconocida');
		}
	}

	public function getViewField()
	{
		switch($this->curView)
		{
			case 'monthly':
				return 'day';
			case 'hourly':
				return 'hour';
			case 'weekly':
				return 'weekday(1=m)';
			default:
				throw new exception('vista no reconocida');
		}
	}

	public function resolveMetric()
	{
		$this->metrics = array('up' => '% tiempo activo', 'down' => '% tiempo inactivo', 'ms' => 'tiempo promedio de respuesta (ms)', 'upminutes' => 'minutos activo', 'downminutes' => 'minutos inactivo'
			, 'metered' => '% controlado', 'unmeteredMinutes' => 'minutos no controlados');
		$curMetric = $this->SafeGetParam('metric', 'up');

		if (array_key_exists($curMetric, $this->metrics) == false)
			$curMetric = $this->metrics[0];

		$this->curMetric = $curMetric; 
	}

	public function showMetric()
	{
		echo "<h4>Indicador: &nbsp;&nbsp;&nbsp;" . $this->metrics[$this->curMetric] . "</h4>";
		echo "<small>Otros: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";

		foreach($this->metrics as $metric => $label)
		{
			if ($this->curMetric  != $metric)
				$this->showLink(
						$this->curDataset, $this->curView,
						$metric, $this->metrics[$metric]);
		}
		echo "</small><br>";
	}

	function  resolveDateset($rootPath)
	{
		$this->datasets = $this->GetFiles($rootPath . '/results', 'csv');
		$curFile = $this->SafeGetParam('dataset', '');
		if (in_array($curFile, $this->datasets) == false)
			$curFile = $this->datasets[0];

		$this->curDatasetFilename =  $rootPath . "/results/" . $curFile; 
		$this->curDataset = $curFile; 
	}

	function  showDateset()
	{
		echo "<h4>Dataset: &nbsp;&nbsp;&nbsp;" . $this->curDataset . "</h4>";
		echo "<small>Otros: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";

		foreach($this->datasets as $file)
		{
			if ($this->curDataset  != $file)
				$this->showLink(
					$file, $this->curView,
					$this->curMetric, $file);
		}
		echo "</small><br>";
	}

	function GetFiles($path, $ext = '')
	{
		$ret = array();
		if ($handle = opendir($path))
		{
			while (false !== ($entry = readdir($handle)))
			{
				if (($ext == '' || $this->EndsWith($entry, $ext)) &&
					$entry != '..' && $entry != '.' && is_file($path . '/'. $entry) )
					$ret[] = $entry;
			}
			closedir($handle);
		}
		return $ret;
	}
	public function currentLinkArgs($includeMetric = true)
	{
		return $this->linkArgs($this->curDataset, $this->curView, $this->curMetric, $includeMetric);
	}
	public function linkArgs($curDataset, $curView, $curMetric, $includeMetric = true)
	{
		$ret = "view=" . $curView . "&dataset=" . urlencode($curDataset);
		if ($includeMetric)
			$ret .= "&metric=" . $curMetric;
		return $ret;
	}
	function showLink($curDataset, $curView, $curMetric, $text)
	{
		$url = "?" . $this->linkArgs($curDataset, $curView, $curMetric);
		echo "<a href='" . $url . "'>" . $text . "</a> ";
	}
	function SafeGetParam($param, $default = "")
		{
			$ret = $default;
			if (array_key_exists($param, $_GET))
				$ret = $_GET[$param];
			else if (array_key_exists($param, $_POST))
				$ret = $_POST[$param];
			if (is_array($ret) == false)
				$ret = trim($ret);
			return $ret;
		}


	function EndsWith($haystack, $needle)
	{
		$length = strlen($needle);
		if ($length == 0)
			return true;
		return (substr($haystack, -$length) === $needle);
	}

}