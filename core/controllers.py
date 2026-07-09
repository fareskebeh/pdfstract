import io
from flask import jsonify, request, make_response
import pymupdf
from PIL import Image
import pytesseract
from hashlib import sha256
import secrets
from keymanager.models import ApiKey


def core_routes_init(app):
    
    @app.route("/extract", methods=["POST"])
    def extract_text():
        request_file=request.files.get("pdf")
        
        
        if not request_file:
            return make_response(jsonify({"error": "No file(s) attached"}), 400)    

        authorization_header=request.headers.get('Authorization')
        if not authorization_header:
            return make_response("No authorization header", 401)
        broken_header=authorization_header.split()
        key=broken_header[1] if (len(broken_header) == 2 and broken_header[0]=='Bearer') else None

        if key:
            query_hash= str(sha256(key.encode()).hexdigest())
            match=ApiKey.query.filter(ApiKey.key_hash==query_hash).first()
            if match:
    
                file = request_file.read()
                pdf_stream = io.BytesIO(file)
                doc = pymupdf.open(stream=pdf_stream, filetype="pdf")
                text = ""
                for page in doc:
                    content= page.get_text()
                    if content:
                        text += content + "pdforge_pagebreak"
                    else:
                        pix=page.get_pixmap(dpi=200)
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        ocr_text = pytesseract.image_to_string(img, lang='eng')

                        if ocr_text:
                            text+=ocr_text
                        else:
                            break
                    
                page_lst=text.split("pdforge_pagebreak")
                return jsonify({"text": page_lst})
            else:
                return make_response("Invalid Key", 401)
        else:
            return make_response("Unauthorized", 401)

    '''@app.route("/extract_ocr", methods=["POST"])
    def ocr_extract():
        pdf_file = request.files.get("pdf")
        if not pdf_file:
            return jsonify({"error": "No file"}), 400
        
        pdf_bytes = pdf_file.read()
        doc = pymupdf.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")
        
        full_text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            text = pytesseract.image_to_string(img, lang='eng')
            full_text += f"_p.{page_num+1}\n{text}\n"
        
        return jsonify({"text": full_text, "pages": len(doc)})
        doc.close()'''