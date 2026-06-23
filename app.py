from flask import Flask
from dotenv import load_dotenv
import os
from core.controllers import register_routes

load_dotenv()

app = Flask(__name__)
register_routes(app)

DEBUG=True if os.getenv("DEBUG") == 'True' else False
print(DEBUG)
if __name__ == "__main__":
    app.run(debug=DEBUG, port=8000)