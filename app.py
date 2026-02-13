from flask import Flask, render_template, request, send_file
from weasyprint import HTML
from docx import Document
from pypdf import PdfReader, PdfWriter
import tempfile
import os
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/generate', methods=['POST'])
def generate():
    data = request.form
    files = request.files
    template_key = data.get('template', 'template1')
    submitted_to = data.get('submitted_to', '').strip()
    submitted_designation = data.get('submitted_designation', '').strip()
    output_format = data.get('output_format', 'pdf')
    output_type = data.get('output_type', 'cover')
    cover_type = data.get('cover_type', 'assignment')
    batch = data.get('batch', '').strip()
    section = data.get('section', '').strip()
    session = data.get('session', '').strip()

    # Build a safe filename based on student ID
    raw_id = data.get('student_id', '').strip()
    safe_id = re.sub(r'[^0-9A-Za-z_-]', '', raw_id) or 'assignment'

    if output_type == 'cover' and output_format == 'docx':
        # Generate a simple DOCX version of the cover page
        document = Document()
        heading = 'Lab Report Cover Page' if cover_type == 'lab' else 'Assignment Cover Page'
        no_label = 'Lab Report No.' if cover_type == 'lab' else 'Assignment No.'
        name_label = 'Lab Report Name' if cover_type == 'lab' else 'Assignment Name'
        document.add_heading(heading, level=0)

        document.add_paragraph(f"{no_label}: {data['assignment_no']}")
        document.add_paragraph(f"Course Code: {data['course_code']}")
        document.add_paragraph(f"Course Title: {data['course_title']}")
        document.add_paragraph(f"{name_label}: {data['assignment_name']}")
        document.add_paragraph(f"Date of Submission: {data['submission_date']}")
        document.add_paragraph("")
        document.add_paragraph(f"Student Name: {data['student_name']}")
        document.add_paragraph(f"ID: {data['student_id']}")
        if batch:
            document.add_paragraph(f"Batch: {batch}")
        if section:
            document.add_paragraph(f"Section: {section}")
        if session:
            document.add_paragraph(f"Session: {session}")
        document.add_paragraph("")
        if submitted_to or submitted_designation:
            document.add_paragraph("Submitted to:")
            if submitted_to:
                document.add_paragraph(submitted_to)
            if submitted_designation:
                document.add_paragraph(submitted_designation)

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as docx_file:
            document.save(docx_file.name)
            return send_file(
                docx_file.name,
                as_attachment=True,
                download_name=f"{safe_id}.docx",
            )

    # Decide which HTML template to use for PDF
    if template_key == 'template2':
        template_file = 'cover2.html'
    elif template_key == 'template3':
        template_file = 'cover3.html'
    else:
        template_file = 'cover.html'

    # Always render the cover HTML for PDF generation
    html = render_template(
        template_file,
        assignment_no=data['assignment_no'],
        course_code=data['course_code'],
        course_title=data['course_title'],
        assignment_name=data['assignment_name'],
        submission_date=data['submission_date'],
        student_name=data['student_name'],
        student_id=data['student_id'],
        submitted_to=submitted_to,
        submitted_designation=submitted_designation,
        cover_type=cover_type,
        batch=batch,
        section=section,
        session=session,
    )

    # Generate cover PDF first
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as cover_file:
        HTML(string=html, base_url=request.url_root).write_pdf(cover_file.name)
        cover_path = cover_file.name

    # If only cover page is requested, just return the cover PDF
    if output_type == 'cover':
        return send_file(
            cover_path,
            as_attachment=True,
            download_name=f"{safe_id}.pdf",
        )

    # Otherwise, merge with uploaded assignment (PDF only)
    assignment = files.get('assignment_file')
    if not assignment or assignment.filename == '':
        return "No assignment file provided for merge.", 400

    _, ext = os.path.splitext(assignment.filename)
    ext = ext.lower()

    if ext != '.pdf':
        return "Merging is currently supported for PDF files only. Please export your DOC/DOCX as PDF first.", 400

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as assignment_file:
        assignment.save(assignment_file.name)
        assignment_path = assignment_file.name

    writer = PdfWriter()
    # Add cover pages
    cover_reader = PdfReader(cover_path)
    for page in cover_reader.pages:
        writer.add_page(page)

    # Add assignment pages
    assignment_reader = PdfReader(assignment_path)
    for page in assignment_reader.pages:
        writer.add_page(page)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as merged_file:
        writer.write(merged_file.name)
        return send_file(
            merged_file.name,
            as_attachment=True,
            download_name=f"{safe_id}_with_cover.pdf",
        )

if __name__ == '__main__':
    app.run(debug=True)
