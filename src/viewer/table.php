<?php

class table
{
	public function show($params, $table)
	{
		$range = $params->getViewRange();
		$rangeFrom= $params->getViewRangeFrom();

		echo '<p><table border=1><tr><td>Monitor<td>General';
		for($n = $rangeFrom; $n <= $range; $n++)
			echo('<td>' . $n);
		echo ('<td>Descargar');
		$totalSamples = 0;
		foreach($table as $key => $row)
		{
			echo '<tr>';
			echo '<td>' . $key;
			$totalSamples+=$row[reader::I_SUCCESS] + $row[reader::I_FAILED];
			$this->echoData($row, $params->curMetric);
			for($n = $rangeFrom; $n <= $range; $n++)
				$this->echoData($row['view'][$n], $params->curMetric);
			echo "<td><a href='?download=1&filter=" . $key . "'>csv</a></small>";
		}
		echo '</table>';
		echo "<p><small>Muestras: " . self::formatNumber($totalSamples) . ".</small>";
	}

	public function showdownload()
	{
		echo "<p><small><a href='?download=1'>Descargar .csv</a></small>";
	}
	function echoData($row, $metric)
	{
		switch($metric)
		{
			case 'up':
				$ttl = ($row[reader::I_UPMINUTES]+$row[reader::I_DOWNMINUTES]) ;
				$up = $this->formatp($row[reader::I_UPMINUTES], $ttl);
				break;
			case 'down':
				$ttl = ($row[reader::I_UPMINUTES]+$row[reader::I_DOWNMINUTES]) ;
				$up = $this->formatp($row[reader::I_DOWNMINUTES], $ttl);
				break;
			case 'ms':
				$ttl = $row[reader::I_SUCCESS];
				$up = $this->formatr($row[reader::I_TOTALMS], $ttl);
				break;
			case 'upminutes':
				$up = $row[reader::I_UPMINUTES];
				break;		
			case 'downminutes':
				$up = $row[reader::I_DOWNMINUTES];
				break;		
			case 'metered':
				$ttl = ($row[reader::I_METEREDMINUTES]+$row[reader::I_UNMETEREDMINUTES]) ;
				$up = $this->formatp($row[reader::I_METEREDMINUTES], $ttl);
				break;
			case 'unmeteredMinutes':
				$up = $row[reader::I_UNMETEREDMINUTES];
				break;		
		}
		echo "<td>" . $up ;
	}
	static function formatNumber($n)
	{
	return number_format($n,0,",",".");
	}
	function formatr($data, $ttl)
	{
		if ($ttl == 0)
			return "-";
		else
			return self::formatNumber($data / $ttl);
	}
	function formatp($data, $ttl)
	{
		if ($ttl == 0)
			return "-";
		else
			return (intval($data / $ttl * 10000) / 100) . "%";
	}
}