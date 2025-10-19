## AVBilling - Setup (Windows)

1) Install Python 3.10+ from python.org. Check "Add to PATH".

2) Open PowerShell in the project folder:

```powershell
cd "C:\Users\DELL\Desktop\made by cursor"
```

3) (Optional) Create a virtual environment:

```powershell
py -3 -m venv .venv
./.venv/Scripts/Activate.ps1
```

4) Install dependencies:

```powershell
pip install --upgrade pip
pip install -r AVBilling/requirements.txt
```

5) Verify and run:

```powershell
python AVBilling/test.py
python AVBilling/main.py
```

If `test.py` reports missing packages, install them as suggested and rerun.


