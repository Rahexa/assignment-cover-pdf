from flask import Flask, render_template, request, send_file
from weasyprint import HTML
from PyPDF2 import PdfMerger
import tempfile
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/generate', methods=['POST'])
def generate_pdf():
    data = request.form
    cover_type = data.get('coverType', 'assignment')
    template = 'cover.html' if cover_type == 'assignment' else 'lab_cover.html'

    # Safely get form data with fallback empty string to avoid KeyErrors
    assignment_no = data.get('assignment_no', '')
    course_code = data.get('course_code', '')
    course_title = data.get('course_title', '')
    assignment_name = data.get('assignment_name', '')
    submission_date = data.get('submission_date', '')
    student_name = data.get('student_name', '')
    student_id = data.get('student_id', '')

    html = render_template(template,
                           assignment_no=assignment_no,
                           course_code=course_code,
                           course_title=course_title,
                           assignment_name=assignment_name,
                           submission_date=submission_date,
                           student_name=student_name,
                           student_id=student_id)

    base_path = os.path.abspath(os.path.dirname(__file__))

    # Generate cover page PDF
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as cover_file:
        HTML(string=html, base_url=base_path).write_pdf(cover_file.name)
        cover_path = cover_file.name

    merger = PdfMerger()
    merger.append(cover_path)

    upload_path = None
    if 'assignment_file' in request.files and request.files['assignment_file'].filename:
        uploaded_file = request.files['assignment_file']
        if uploaded_file.mimetype == 'application/pdf':
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as upload_file:
                uploaded_file.save(upload_file.name)
                merger.append(upload_file.name)
                upload_path = upload_file.name
        else:
            os.unlink(cover_path)
            return {"error": "Uploaded file must be a PDF"}, 400

    # Write merged PDF
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as output_file:
        merger.write(output_file)
        output_path = output_file.name

    merger.close()

    # Clean up temp files
    os.unlink(cover_path)
    if upload_path:
        os.unlink(upload_path)

    return send_file(output_path, as_attachment=True, download_name=f"{cover_type}_cover.pdf")


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
