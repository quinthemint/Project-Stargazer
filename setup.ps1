$venvPath = "venv"

if (!(Test-Path $venvPath)) {
    python -m venv $venvPath
}

& "$venvPath\Scripts\Activate.ps1"
pip install --upgrade pip
pip install -r requirements.txt
