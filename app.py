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
    
    html = render_template(template,
        assignment_no=data['assignment_no'],
        course_code=data['course_code'],
        course_title=data['course_title'],
        assignment_name=data['assignment_name'],
        submission_date=data['submission_date'],
        student_name=data['student_name'],
        student_id=data['student_id']
        # ✅ teacher_name বাদ দেওয়া হয়েছে
    )

    base_path = os.path.abspath(os.path.dirname(__file__))

    # Generate cover page PDF
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as cover_file:
        HTML(string=html, base_url=base_path).write_pdf(cover_file.name)
        cover_path = cover_file.name

    # Initialize PDF merger
    merger = PdfMerger()
    merger.append(cover_path)

    # Check if a file was uploaded and merge it
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

    # Close merger after writing
    merger.close()

    # Clean up temporary files
    os.unlink(cover_path)
    if upload_path:
        os.unlink(upload_path)

    return send_file(output_path, as_attachment=True, download_name=f"{cover_type}_cover.pdf")

if __name__ == '__main__':
    app.run(debug=True)
