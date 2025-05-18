# Project-Stargazer

**CSC 480 Final Project**  
An interactive, user friendly stargazing tool built on a knowledge base of star information.

---

## Set up venv

### For **PowerShell**

    powershell -ExecutionPolicy Bypass -File setup.ps1  
    .\venv\Scripts\Activate.ps1

Then start the local frontend with:

    streamlit run your_app.py

---

### For **Linux systems**

    make setup  
    make run

---

## Notes

- Once venv is set, re-use it instead of reinstalling every time  
- Make sure to add a new API key to `.env` if running locally
