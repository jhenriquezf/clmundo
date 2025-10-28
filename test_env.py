# test_env.py
from dotenv import load_dotenv
from pathlib import Path
from decouple import config

# Cargar el archivo .env explícitamente
env_path = Path('C:/Desarrollos/clmundo/.env')
load_dotenv(dotenv_path=env_path)

print("GOOGLE_MAPS_API_KEY:", config('GOOGLE_MAPS_API_KEY', default='No seteada'))
print("TWILIO_ACCOUNT_SID:", config('TWILIO_ACCOUNT_SID', default='No seteada'))
print("TWILIO_AUTH_TOKEN:", config('TWILIO_AUTH_TOKEN', default='No seteada'))