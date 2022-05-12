import os
import fitz
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
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		resp = jsonify({'message' : 'File successfully uploaded'})
		if filename.rsplit('.', 1)[1].lower()=="pdf":
			print("")
			with pdfplumber.open('uploads/' + filename) as pdf:
				page = pdf.pages[5]
				#session['text'] = page.extract_text()
				info = page.extract_table()
				text = ''
				for arr in info:
					for word in arr:
						if word is not None:
							new_word = word.replace("\n", ",")
							text += word + " "
					text += "\n"
				session['text'] = text
			# doc = fitz.open('uploads/' + filename)
			# for page in doc:
			# 	session['text'] = page.get_text("text")
	
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
	answer = QueryAnswerer().getAnswer(text, query)
	resp = jsonify({'answer' : answer})
	resp.status_code = 200
	return resp 

if __name__ == "__main__":
	app.run(debug=False, host='0.0.0.0')