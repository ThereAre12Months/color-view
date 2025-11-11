try {
	Invoke-Expression "$PSScriptRoot/.venv/Scripts/activate.ps1"
	python "$PSScriptRoot/main.py"
}
finally {
	deactivate
}
