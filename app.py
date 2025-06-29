
from flask import Flask, render_template, request, send_file
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from io import BytesIO
import tempfile

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_cover():
    # Get form data
    student_name = request.form.get('student_name', '')
    course_name = request.form.get('course_name', '')
    assignment_title = request.form.get('assignment_title', '')
    date = request.form.get('date', '')
    professor_name = request.form.get('professor_name', '')
    
    # Create PDF in memory
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Add logo if exists
    logo_path = os.path.join('static', 'images', 'puclogo.png')
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 50, height - 150, width=100, height=100)
    
    # Add text content
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredText(width/2, height - 200, assignment_title)
    
    p.setFont("Helvetica", 16)
    p.drawCentredText(width/2, height - 250, f"Student: {student_name}")
    p.drawCentredText(width/2, height - 280, f"Course: {course_name}")
    p.drawCentredText(width/2, height - 310, f"Professor: {professor_name}")
    p.drawCentredText(width/2, height - 340, f"Date: {date}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{assignment_title}_cover.pdf",
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
