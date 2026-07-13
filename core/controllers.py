import io
from flask import jsonify, request, make_response
import pymupdf
from PIL import Image
import pytesseract
from hashlib import sha256
import secrets
from keymanager.models import ApiKey
from auth.models import User
from payments.models import Plan
from db.extensions import db

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
                user= User.query.get(match.user_id)
                user_plan= Plan.query.get(user.plan_id)
                if user.master_quota >= user_plan.quota_limit:
                    return make_response({"message": "Limit has been reached, Upgrade your plan or wait until the quota resets"}, 429)
                elif user_plan.quota_limit < user.master_quota + len(doc):
                    return make_response({"message": "You do not have enough quota to process this file, Upgrade your plan or wait until the quota resets"}, 429)
                
                text = ""
                
                user.master_quota += len(doc)
                db.session.commit()
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