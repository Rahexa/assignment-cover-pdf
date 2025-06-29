
from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black
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
        assignment_no = data.get('assignment_no', '01')
        course_code = data.get('course_code', 'MGT 251')
        assignment_title = data.get('assignment_name', 'Regular Assignment')
        student_name = data.get('student_name', 'Mohammad Hafizur Rahman Sakib')
        student_id = data.get('student_id', '0222210005101118')
        course_name = data.get('course_title', 'Organizational Behavior')
        professor_name = data.get('submitted_to', 'Tashin Hossain')
        submission_date = data.get('submission_date', '29-06-2025')
        print(f"Generating PDF with title: {assignment_title}")

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_file:
            print(f"Creating PDF at: {pdf_file.name}")
            p = canvas.Canvas(pdf_file.name, pagesize=letter)
            width, height = letter

            # Set margins
            margin = 50
            content_width = width - 2 * margin

            # Draw border
            p.setStrokeColor(black)
            p.setLineWidth(2)
            p.rect(margin, margin, content_width, height - 2 * margin)

            # Header with logo and university info
            y_pos = height - 120
            
            # University name (left)
            p.setFont("Times-Roman", 23)
            p.drawString(margin + 40, y_pos, "PREMIER UNIVERSITY")
            
            # Logo (center)
            logo_path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'puclogo.png')
            if os.path.exists(logo_path):
                try:
                    p.drawImage(logo_path, width/2 - 35, y_pos - 10, width=70, height=70)
                except Exception as e:
                    print(f"Error drawing image: {e}")
            
            # Department name (right)
            p.setFont("Times-Italic", 16)
            dept_text = "Department of Computer Science & Engineering"
            dept_width = p.stringWidth(dept_text, "Times-Italic", 16)
            p.drawString(width - margin - dept_width - 40, y_pos, dept_text)

            # Dotted line
            y_pos -= 80
            p.setDash(2, 2)
            p.setLineWidth(2)
            p.line(margin + 20, y_pos, width - margin - 20, y_pos)
            p.setDash()  # Reset to solid line

            # Title "Assignment"
            y_pos -= 60
            p.setFont("Times-Bold", 23)
            title_text = "Assignment"
            title_width = p.stringWidth(title_text, "Times-Bold", 23)
            p.drawString(width/2 - title_width/2, y_pos, title_text)
            
            # Underline the title
            p.setLineWidth(1)
            p.line(width/2 - title_width/2, y_pos - 5, width/2 + title_width/2, y_pos - 5)

            # Assignment information
            y_pos -= 50
            p.setFont("Times-Roman", 16)
            
            info_items = [
                ("Assignment No.", assignment_no),
                ("Course Code", course_code),
                ("Course Title", course_name),
                ("Assignment Name", assignment_title),
                ("Date of Submission", submission_date)
            ]
            
            for label, value in info_items:
                p.drawString(margin + 40, y_pos, label)
                p.drawString(margin + 200, y_pos, ":")
                p.setFont("Times-Bold", 16)
                p.drawString(margin + 220, y_pos, value)
                p.setFont("Times-Roman", 16)
                y_pos -= 25

            # "Submitted by" section
            y_pos -= 30
            p.setFont("Times-Bold", 16)
            section_text = "Submitted by"
            p.drawString(margin + 40, y_pos, section_text)
            # Underline
            section_width = p.stringWidth(section_text, "Times-Bold", 16)
            p.line(margin + 40, y_pos - 5, margin + 40 + section_width, y_pos - 5)

            # Student information table
            y_pos -= 40
            table_x = margin + 40
            table_y = y_pos
            table_width = 380
            row_height = 25
            
            # Table data
            table_data = [
                ("Name", student_name),
                ("ID", student_id),
                ("Program", "B.Sc. in CSE"),
                ("Batch", "41"),
                ("Section", "C"),
                ("Session", "Fall 2025")
            ]
            
            p.setFont("Times-Roman", 14)
            
            # Draw table
            for i, (label, value) in enumerate(table_data):
                row_y = table_y - i * row_height
                
                # Draw cell borders
                p.setLineWidth(1)
                p.rect(table_x, row_y - row_height, 80, row_height)  # Label cell
                p.rect(table_x + 80, row_y - row_height, table_width - 80, row_height)  # Value cell
                
                # Draw text
                p.drawString(table_x + 5, row_y - row_height + 8, label)
                p.drawString(table_x + 85, row_y - row_height + 8, value)

            # Remarks box
            remarks_x = table_x + table_width + 30
            remarks_y = table_y
            remarks_width = 150
            remarks_height = 120
            
            p.setLineWidth(2)
            p.rect(remarks_x, remarks_y - remarks_height, remarks_width, remarks_height)
            
            # Remarks title
            p.setFont("Times-Bold", 14)
            remarks_title = "Remarks"
            remarks_title_width = p.stringWidth(remarks_title, "Times-Bold", 14)
            p.drawString(remarks_x + remarks_width/2 - remarks_title_width/2, remarks_y - 20, remarks_title)
            
            # Line under remarks title
            p.setLineWidth(1)
            p.line(remarks_x + 5, remarks_y - 30, remarks_x + remarks_width - 5, remarks_y - 30)

            # "Submitted to" section
            y_pos = table_y - len(table_data) * row_height - 80
            p.setFont("Times-Bold", 16)
            section_text = "Submitted to"
            p.drawString(margin + 40, y_pos, section_text)
            # Underline
            section_width = p.stringWidth(section_text, "Times-Bold", 16)
            p.line(margin + 40, y_pos - 5, margin + 40 + section_width, y_pos - 5)

            # Submitted to information
            y_pos -= 30
            p.setFont("Times-Bold", 14)
            p.drawString(margin + 40, y_pos, "Submitted to:")
            
            y_pos -= 20
            p.setFont("Times-Roman", 14)
            submitted_to_lines = [
                professor_name,
                "Lecturer, CSE Department",
                "Premier University",
                "Chittagong"
            ]
            
            for line in submitted_to_lines:
                p.drawString(margin + 40, y_pos, line)
                y_pos -= 18

            p.showPage()
            p.save()
            print("PDF generated successfully")
            return send_file(pdf_file.name, as_attachment=True, download_name="assignment_cover_page.pdf")

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
