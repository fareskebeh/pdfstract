from flask import jsonify, request, make_response
import pymupdf

def register_routes(app):
    @app.route('/')
    def index():
        return jsonify({"text":"index route"})
    
    @app.route("/extract", methods=["POST"])
    def extract_text():
        request_file=request.files.get("pdf")
        if not request_file:
            return make_response(jsonify({"error": "No file(s) attached"}), 400)        
        file = pymupdf.open(request_file)
        out = open("output.txt", "wb")
        for page in file:
            text = page.get_text().encode("utf8")
            out.write(text)
            out.write(bytes((12,)))
        out.close()
        output = out.read()
        return jsonify({"text": output})