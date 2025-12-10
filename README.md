
markdown

# 🎵 Modern Jazz - Java Code Modernizator

Automated Java code modernization using StackSpot AI.

## 🚀 Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run setup check
python setup.py
2. Configure Credentials
bash

# Copy example file
copy secrets-example.json secrets.json

# Edit secrets.json with your credentials
notepad secrets.json
secrets.json structure:

json

{
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "realm": "zup"
}
3. Run Modernization
bash

python main.py
📁 Project Structure
modern-jazz/ 
├── application/ # Application services 
│ ├── modernization_service.py 
│ └── report_generator.py 
├── config/ # Configuration 
│ └── settings.py 
├── domain/ # Domain entities 
│ ├── entities.py 
│ └── exceptions.py 
├── infrastructure/ # External integrations 
│ ├── file_system.py 
│ └── stackspot_client.py 
├── main.py # Entry point 
├── setup.py # Setup validation 
├── secrets.json # Your credentials (gitignored) 
└── secrets-example.json # Template

🔧 Configuration
Edit main.py to configure:

python

# Java project path
java_project_path = r"C:\path\to\your\java\project"

# Save changes (False for dry-run)
save_changes = True
📊 Output
Console: Real-time progress and statistics
Report: modernization_report.json with detailed results
🛠️ Troubleshooting
Credentials not found
bash

# Run setup check
python setup.py

# Verify secrets.json exists
dir secrets.json
Import errors
bash

# Reinstall dependencies
pip install -r requirements.txt
📝 License
MIT

## 🎯 Como Usar ### Passo 1: Executar Setup ```bash cd C:\Users\marcelo.gomes\gomesmr\Hackathon\modern-jazz python setup.py
Passo 2: Configurar Credentials
bash

# Se secrets.json não existir, será criado automaticamente
# Edite e adicione suas credenciais
notepad secrets.json
Passo 3: Executar Modernização
bash

python main.py
🔍 Debug
Se ainda tiver problemas, execute:

bash

# Verificar configuração
python -c "from config.settings import settings; print(settings)"

# Verificar se arquivo existe
python -c "from config.settings import settings; print(f'Exists: {settings.CREDENTIALS_PATH.exists()}')"
