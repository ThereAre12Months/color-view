try {
	Get-Command python
	if (! $LASTEXITCODE -eq 0) {
		throw "ERROR: python not found on PATH"
	}

	if (!(Test-Path "$PSScriptRoot/.venv/")) {
		Write-Output "INFO: creating virtual environment"
		python -m venv "$PSScriptRoot/.venv"
	}
	Invoke-Expression "$PSScriptRoot/.venv/Scripts/activate.ps1"

	Write-Output "INFO: installing/upgrading pip and requirements"
	python -m pip install --upgrade pip
	python -m pip install --upgrade -r "$PSScriptRoot/requirements.txt"
}
finally {
	deactivate
}
