from flask import Flask
from api_v1_0 import api as api_v1_0

app = Flask(__name__)
app.register_blueprint(api_v1_0, url_prefix='/api/v1.0')

