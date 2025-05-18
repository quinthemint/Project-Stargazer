VENV_NAME = venv
PYTHON = python3

.PHONY: setup run clean

setup:
	@test -d $(VENV_NAME) || $(PYTHON) -m venv $(VENV_NAME)
	. $(VENV_NAME)/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

run:
	. $(VENV_NAME)/bin/activate && streamlit run app.py

clean:
	rm -rf $(VENV_NAME)
