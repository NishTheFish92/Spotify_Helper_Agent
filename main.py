from src import auth
from dotenv import load_dotenv
import os
load_dotenv()
refresh_token = os.getenv("refresh_token")
print(auth.refresh_access_token(refresh_token))


