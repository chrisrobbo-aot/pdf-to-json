### Overview
Leverages OpenAI to convert data from PDF to JSON.

### Setup

#### 1. Create a virtual environment

##### For macOS/Linux:
```bash
python3 -m venv venv
```

##### For Windows:
```powershell
python -m venv venv
```

#### 2. Activate the virtual environment

##### For macOS/Linux:
```bash
source venv/bin/activate
```

##### For Windows:
```powershell
.\venv\Scripts\activate
```

#### 3. Install requirements
```bash
pip install -r requirements.txt
```

#### 4. Add OpenAI API key to the environment

##### For macOS/Linux:
```bash
export OPENAI_API_KEY=<your-openai-api-key>
```

##### For Windows (CMD):
```cmd
set OPENAI_API_KEY=<your-openai-api-key>
```

##### For Windows (PowerShell):
```powershell
$env:OPENAI_API_KEY="<your-openai-api-key>"
```

#### 5. Run the Python file to generate the JSON
```bash
python app.py
```