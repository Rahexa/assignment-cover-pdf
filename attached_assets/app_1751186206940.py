from flask import Flask, render_template, request, send_file
from weasyprint import HTML
import tempfile

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/generate', methods=['POST'])
def generate_pdf():
    data = request.form
    html_content = render_template("cover.html", data=data)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_file:
        HTML(string=html_content, base_url='.').write_pdf(pdf_file.name)
        return send_file(pdf_file.name, as_attachment=True, download_name="cover_page.pdf")

if __name__ == '__main__':
    app.run(debug=True)
