"""
Helper script to generate sample test resumes (DOCX and PDF text) for validation.
"""
import os
import docx

def create_sample_docx(dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    doc = docx.Document()
    doc.add_heading("Karan Gupta", level=0)
    doc.add_paragraph("Email: karan.gupta@example.com | Phone: +91 9876543210 | Location: New Delhi, India")
    
    doc.add_heading("Education", level=1)
    doc.add_paragraph("Delhi Technological University (DTU)\nBachelor of Technology in Computer Science & Engineering\nCurrent Semester: 6th Semester | Expected Graduation: 2026")
    
    doc.add_heading("Technical Skills", level=1)
    doc.add_paragraph("Programming Languages: Python, C++, SQL, JavaScript\nFrameworks & Libraries: PyTorch, TensorFlow, Scikit-learn, Flask, Pandas, NumPy\nTools & Platforms: Docker, Git, Linux, AWS, Jupyter\nCore Concepts: Machine Learning, Deep Learning, Statistics, Data Structures, Algorithms, REST APIs")
    
    doc.add_heading("Projects", level=1)
    doc.add_paragraph("1. Medical Image Segmentation using CNNs (PyTorch, OpenCV)\n- Developed a U-Net architecture in PyTorch to segment cellular anomalies with 94.2% IoU.\n- Integrated with a Flask REST API microservice and containerized with Docker.")
    doc.add_paragraph("2. Algorithmic Trading Predictor (Python, Scikit-learn, Pandas)\n- Implemented Random Forest and LSTM time-series forecasting on historical equities.")
    
    doc.add_heading("Interests & Aspirations", level=1)
    doc.add_paragraph("Artificial Intelligence, Machine Learning, Data Science, Software Development. Seeking Full-time roles.")
    
    doc.save(dest_path)
    print(f"Sample DOCX resume created at: {dest_path}")

if __name__ == "__main__":
    resumes_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_resumes")
    create_sample_docx(os.path.join(resumes_dir, "sample_resume_karan.docx"))
