<?php

class reader
{
	const I_SUCCESS = 0;
	const I_FAILED = 1;
	const I_DOWNMINUTES = 2;
	const I_UPMINUTES = 3;
	const I_TOTALMS = 4;
	const I_METEREDMINUTES = 5;
	const I_UNMETEREDMINUTES = 6;
	const I_SIZE = 7;
	private $rootPath = "";

	public function reader($rootPath)
	{
		$this->rootPath = $rootPath;
	}

	function incrementSuccess(&$mdata, $mins, $ms)
	{
			$mdata[reader::I_SUCCESS] ++;
			$mdata[reader::I_UPMINUTES] += $mins;
			$mdata[reader::I_TOTALMS] += $ms;
			$mdata[reader::I_METEREDMINUTES] += $mins;
	}
	function incrementFailure(&$mdata, $mins)
	{
			$mdata[reader::I_FAILED]++;
			$mdata[reader::I_DOWNMINUTES]+= $mins;
			$mdata[reader::I_METEREDMINUTES] += $mins;
	}
	function incrementUnmetered(&$mdata, $mins)
	{
			$mdata[reader::I_UNMETEREDMINUTES] += $mins;
	}

	function get($index, $arr, $field)
	{
		return $arr[$index[$field]];
	}
	function getarr($number, $rangeFrom)
	{
	 if ($number == 0)
		return array_fill(0, reader::I_SIZE, 0);
		
		$ret = array();
		for($n = $rangeFrom; $n <= $number; $n++)
			$ret[$n] = $this->getarr(0, 0);
		return $ret;
	}

	function read($params)
	{
		$file = $params->curDatasetFilename;
		$range = $params->getViewRange();
		$rangeFrom= $params->getViewRangeFrom();
		$field = $params->getViewField();


		$table = array();
		$handle = fopen($file, "r");

		$headers = fgetcsv($handle, 0, ";");
		$index = array();
		for ($c=0; $c < sizeof($headers); $c++) 
		{
				$index[$headers[$c]] = $c;
		}

		while (($data = fgetcsv($handle, 0, ";")) !== FALSE) 
		{
			$monitor = $this->get($index, $data, 'owner') . '-' . $this->get($index, $data, 'monitor');
			if (!array_key_exists($monitor, $table))
			{
				$table[$monitor] = $this->getarr(0, 0);
				$table[$monitor]['view'] = $this->getarr($range, $rangeFrom);
			}
			$mdata = &$table[$monitor];

			$mins = $this->get($index, $data, 'interval(mins)');
			$success = $this->get($index, $data, 'success');
			$day = $this->get($index, $data, $field);
			if ($success == "1")
			{
				$ms = $this->get($index, $data, 'responseMs');
				$this->incrementSuccess($mdata, $mins, $ms);
				$this->incrementSuccess($mdata['view'][$day], $mins, $ms);
			}
			else if ($success == "0")
			{
				$this->incrementFailure($mdata, $mins);
				$this->incrementFailure($mdata['view'][$day], $mins);
			}
			else if ($success == "")
			{
				$this->incrementUnmetered($mdata, $mins);
				$this->incrementUnmetered($mdata['view'][$day], $mins);
			}
		}
		fclose($handle);
		return $table;
	}
}