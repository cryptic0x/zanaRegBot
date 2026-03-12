import gspread
import os
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)

client = gspread.authorize(creds)

files = client.list_spreadsheet_files()

load_dotenv()



print(files)

print(os.getenv("TELEGRAM_BOT_TOKEN"))