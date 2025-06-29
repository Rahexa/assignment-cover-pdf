
from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import tempfile
from PIL import Image

app = Flask(__name__)

@app.route('/')
def index():
    print(f"Current working directory: {os.getcwd()}")
    print("Rendering index.html")
    return render_template("index.html")

@app.route('/generate_cover', methods=['POST'])
def generate_cover():
    print("Reached /generate_cover route")
    print(f"Form data: {request.form}")
    try:
        data = request.form
        assignment_title = data.get('assignment_name', 'Sample Assignment')
        student_name = data.get('student_name', 'Unknown Student')
        course_name = data.get('course_title', 'Unknown Course')
        professor_name = data.get('submitted_to', 'Unknown Professor')
        print(f"Generating PDF with title: {assignment_title}")

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_file:
            print(f"Creating PDF at: {pdf_file.name}")
            p = canvas.Canvas(pdf_file.name, pagesize=letter)
            width, height = letter

            logo_path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'puclogo.png')
            print(f"Checking logo path: {logo_path}")
            if os.path.exists(logo_path):
                try:
                    img = Image.open(logo_path)
                    print(f"Image opened successfully: {img.format}, {img.size}")
                    p.drawImage(logo_path, 50, height - 150, width=100, height=100)
                except Exception as e:
                    print(f"Error drawing image: {e}")
                    p.drawString(50, height - 150, "Logo not available")
            else:
                print(f"File not found: {logo_path}")
                p.drawString(50, height - 150, "Logo not found")

            p.setFont("Helvetica-Bold", 24)
            p.drawCentredString(width / 2, height - 200, assignment_title)
            p.setFont("Helvetica", 16)
            p.drawCentredString(width / 2, height - 250, f"Student: {student_name}")
            p.drawCentredString(width / 2, height - 280, f"Course: {course_name}")
            p.drawCentredString(width / 2, height - 310, f"Professor: {professor_name}")

            p.showPage()
            p.save()
            print("PDF generated successfully")
            return send_file(pdf_file.name, as_attachment=True, download_name="cover_page.pdf")

    except Exception as e:
        print(f"Error generating PDF: {e}")
        return "Error generating PDF. Check logs for details.", 500

@app.route('/test_image')
def test_image():
    logo_path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'puclogo.png')
    print(f"Testing image path: {logo_path}")
    if os.path.exists(logo_path):
        return send_file(logo_path)
    return "Image not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
