import os
import io
import fitz
import urllib.request
import pdfplumber
import PyPDF2
from app import app
from flask import Flask, request, redirect, jsonify
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['txt', 'pdf'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/file-upload', methods=['POST'])
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
			
			doc = fitz.open('uploads/' + filename)
			for page in doc:
				text = page.getText("text")
				print(text)
			#all_text = None
			#with pdfplumber.open('uploads/' + filename,"rb") as pdf:
				""" pdfReader = PyPDF2.PdfFileReader(pdf,strict=False)
				number_of_pages = pdfReader.getNumPages()
				page = pdfReader.getPage(0)
				single_page_text = page.extractText()
				print( single_page_text ) """
	
		resp.status_code = 201
		return resp
	else:
		resp = jsonify({'message' : 'Allowed file types are txt, pdf'})
		resp.status_code = 400
		return resp

if __name__ == "__main__":
	app.run()