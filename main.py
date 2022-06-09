import json
import pdfplumber
from app import app
from flask import request, jsonify, session
from werkzeug.utils import secure_filename
import pymongo
from bson import ObjectId, json_util

from bert import QueryAnswerer

ALLOWED_EXTENSIONS = set(['txt', 'pdf'])

mongoCluster = pymongo.MongoClient(app.config.get('MONGO_URI'))

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/fileUpload', methods=['POST'])
def upload_file():
	if 'file' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	file = request.files['file']
	if file.filename == '':
		resp = jsonify({'message' : 'No file selected for uploading'})
		resp.status_code = 400
		return resp
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		resp = jsonify({'message' : 'File successfully uploaded'})
		if filename.rsplit('.', 1)[1].lower()=="pdf":
			text = ''
			with pdfplumber.open(file) as pdf:
				for page in pdf.pages:
					info = page.extract_table()
					try:
						for arr in info:
							for word in arr:
								if word is not None:
									new_word = word.replace('\n', '.')
									text += new_word + " "
							text += "\n"
					except Exception as e:
						info = page.extract_text()
						text += "\n" + info
				result = mongoCluster.get_database('db').get_collection('pdftext').insert_one({'data':text})
				session["object_id"] = json.loads(json_util.dumps(result.inserted_id))['$oid']
				print(json.loads(json_util.dumps(result.inserted_id))['$oid'])
				#datastore.setText(text)
			
		resp.status_code = 201
		return resp
	else:
		resp = jsonify({'message' : 'Allowed file types are txt, pdf'})
		resp.status_code = 400
		return resp

@app.route('/getAnswer', methods=['POST'])
def getAnswer():
	#text = datastore.getText()
	text = mongoCluster.get_database('db').get_collection('pdftext').find_one({'_id': ObjectId(session['object_id'])})['data']
	print(text)
	query = request.args.get('query')
	if text == None or query == None:
		resp = None
		if text == None:
			resp = jsonify({'error': 'context is null'})
		else:
			resp = jsonify({'error': 'question is null'})
		resp.status_code = 401
		return resp
	answer = QueryAnswerer().getAnswer(text, query)
	resp = jsonify({'answers' : answer})
	resp.status_code = 200
	return resp 

if __name__ == "__main__":
	app.run(debug=False, host='0.0.0.0')