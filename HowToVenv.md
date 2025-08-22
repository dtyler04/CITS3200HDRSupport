# How to Set Up a Python Virtual Environment (venv) and Install Requirements

## 1. Creating a Virtual Environment

### Windows
Open Command Prompt and run:
```
python -m venv venv
```

### Mac/Linux
Open Terminal and run:
```
python3 -m venv venv
```

*This command creates a folder named `venv` containing a clean Python environment, isolated from your system Python and other projects.*

## 2. Activating the Virtual Environment

### Windows
```
venv\Scripts\activate
```

### Mac/Linux
```
source venv/bin/activate
```

*Activating the virtual environment changes your shell so that Python and pip commands use the isolated environment. This ensures you install and run packages only for this project.*

## 3. Installing Requirements
Once the virtual environment is activated, run:
```
pip install -r requirements.txt
```

*This installs all the dependencies listed in `requirements.txt` into your virtual environment, keeping them separate from your global Python installation.*

## 4. Deactivating the Virtual Environment
To deactivate, simply run:
```
deactivate
```

*This returns your shell to the normal system Python environment.*

---
This ensures your dependencies are isolated and your project runs consistently across different systems.
