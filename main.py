import os
import pdfplumber
from app import app
from flask import request, jsonify, session
from werkzeug.utils import secure_filename

from bert import QueryAnswerer

ALLOWED_EXTENSIONS = set(['txt', 'pdf'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/fileUpload', methods=['POST'])
def upload_file():
	# check if the post request has the file part
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
		print(filename)
		resp = jsonify({'message' : 'File successfully uploaded'})
		if filename.rsplit('.', 1)[1].lower()=="pdf":
			print("")
			with pdfplumber.open(file) as pdf:
				page = pdf.pages[5]
				info = page.extract_table()
				text = ''
				for arr in info:
					for word in arr:
						if word is not None:
							new_word = word.replace("\n", ",")
							text += new_word + " "
					text += "\n"
				session['text'] = text
			
		resp.status_code = 201
		return resp
	else:
		resp = jsonify({'message' : 'Allowed file types are txt, pdf'})
		resp.status_code = 400
		return resp

@app.route('/getAnswer', methods=['POST'])
def getAnswer():
	text = session.pop('text', None)
	session['text'] = text
	query = request.args.get('query')
	print(text)
	print('-------------')
	print(query)
	if text == None or query == None:
		resp = jsonify({'error': 'question or context is null'})
		resp.status_code = 401
		return resp
	answer = QueryAnswerer().getAnswer(text, query)
	resp = jsonify({'answer' : answer})
	resp.status_code = 200
	return resp 

if __name__ == "__main__":
	app.run(debug=False, host='0.0.0.0')