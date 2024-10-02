from flask import Flask, render_template, request, send_file
import os
import datetime
from fpdf import FPDF  # for creating PDFs
import wikipedia
import requests  # For interacting with Gemini AI

app = Flask(__name__)

# Configure your Gemini AI API Key
GEMINI_API_KEY = "AIzaSyDPb4Ktg8AC9WOuvJjH8YvZciViP9tn6eE"  # Replace with your actual API key
GEMINI_BASE_URL = "https://gemini.google.com/"  # Replace with actual Gemini AI API URL


class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Study Assistant Results', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask():
    question = request.form.get('question')
    task_type = request.form.get('task_type')  # Get the task type (math, english, wikipedia)

    response = ""

    if task_type == "wikipedia":
        # Wikipedia functionality
        try:
            topic = question.replace("wikipedia", "").strip()
            response = wikipedia.summary(topic, sentences=2)
        except wikipedia.exceptions.DisambiguationError as e:
            response = f"Multiple topics found for {topic}. Please be more specific."
        except wikipedia.exceptions.PageError:
            response = f"No page found for {topic}."

    elif task_type == "math":
        # Call Gemini AI's Math solving endpoint
        response = call_gemini_ai(question, "math")

    elif task_type == "english":
        # Call Gemini AI's English assistance endpoint
        response = call_gemini_ai(question, "english")

    else:
        response = "Sorry, I can't help with that yet."

    return render_template('result.html', question=question, response=response)


def call_gemini_ai(question, task_type):
    """
    Call Gemini AI API with a task (e.g., math problem solving or English assistance)
    """
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "question": question,
        "task_type": task_type  # "math" or "english"
    }

    try:
        response = requests.post(f"{GEMINI_BASE_URL}/ai/assist", json=data, headers=headers)
        if response.status_code == 200:
            result = response.json().get('answer', 'No answer found')
            return result
        else:
            return f"Error fetching response from Gemini AI: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Error: Unable to connect to Gemini AI - {str(e)}"


@app.route('/download', methods=['POST'])
def download():
    question = request.form.get('question')
    response = request.form.get('response')

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Question: {question}", ln=True)
    pdf.cell(200, 10, txt=f"Response: {response}", ln=True)

    filename = f"result_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)

    return send_file(filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
