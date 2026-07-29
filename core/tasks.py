import io
import pymupdf
from PIL import Image
import pytesseract
from auth.models import User
from payments.models import Plan
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()

DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

def extract_text(fp, user_id):
    session = Session()
    try:
        with open(fp, 'rb') as f:
            doc = pymupdf.open(fp, filetype="pdf")
            
            user = session.query(User).get(user_id)
            if not user:
                return {"error": "User not found"}
            
            user_plan = session.query(Plan).get(user.plan_id)
            
            if user.master_quota >= user_plan.quota_limit:
                return {"error": "Quota limit reached"}
            
            if user_plan.quota_limit < user.master_quota + len(doc):
                return {"error": "Not enough quota for this file"}
            text = ""
            for page in doc:
                content = page.get_text()
                if content:
                    text += content + "pagebreak_pagebreak"
                else:
                    pix = page.get_pixmap(dpi=128)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    ocr_text = pytesseract.image_to_string(img, lang='eng')
                    if ocr_text:
                        text += ocr_text
            
            user.master_quota += len(doc)
            session.commit()
            
            page_lst = text.split("pagebreak_pagebreak")
            return {"text": page_lst}
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
        if os.path.exists(fp):
            os.remove(fp)