from flask import Flask

app = Flask(__name__)
app.secret_key = "secret key"
app.config['MONGO_URI'] = "mongodb+srv://Riskcovry2022:Riskcovry2022@cluster0.1i2yo.mongodb.net/?retryWrites=true&w=majority"
#app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024