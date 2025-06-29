from flask import Flask, render_template, request, send_file
from weasyprint import HTML
import tempfile

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/generate', methods=['POST'])
def generate():
    data = request.form
    html = render_template('cover.html',
        assignment_no=data['assignment_no'],
        course_code=data['course_code'],
        course_title=data['course_title'],
        assignment_name=data['assignment_name'],
        submission_date=data['submission_date'],
        student_name=data['student_name'],
        student_id=data['student_id']
    )
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_file:
        HTML(string=html, base_url=".").write_pdf(pdf_file.name)
        return send_file(pdf_file.name, as_attachment=True, download_name="assignment_cover_page.pdf")

if __name__ == '__main__':
    app.run(debug=True)
