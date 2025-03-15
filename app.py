from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "123"

# Configure Gemini API Key
GEMINI_API_KEY = "AIzaSyBTBHO9FNMvOhKGRqoM3sE1UqWRvgkvNmc"
genai.configure(api_key=GEMINI_API_KEY)

@app.route('/')
def index():
    session['conversation'] = []  # Initialize conversation history
    return render_template('index.html')

@app.route('/survey')
def survey():
    return render_template('survey.html')

@app.route('/meditation')
def meditation():
    return render_template('meditation.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.json.get('message')

    try:
        # Define the system instruction
        system_instruction = "You are an AI cognitive therapist. Act normal and answer the user's questions. Generate content without formatting based on the user's input. Don't use long sentences."
        # Initialize the generative model
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=system_instruction)
        # Structure the prompt as a conversation
        prompt = user_message
        # Generate response using the generative model with the structured prompt
        response = model.generate_content(prompt)
        # Extract AI response
        ai_response = response.text if response.text else "I'm here to help. Can you tell me more?"
        return jsonify({'response': ai_response})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'response': "Sorry, something went wrong. Please try again later."})
    
def generate_feedback(survey_data, mood_score):
    prompt = f"The user's mood score is {mood_score}/15. Here are the detailed scores:\n"
    for question, score in survey_data.items():
        prompt += f"{question}: {score}\n"
    prompt += "Provide short feedback within 100 words and no formatting based on these scores and suggest ways to improve the user's mood. The questions are: 1. How often do you feel stressed? 2. How satisfied are you with your social life? 3. How would you rate your overall mood? Include tips to improve mood and reduce stress if scores are low"
    try:

        system_instruction = "{prompt}"
        # Initialize the generative model
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            )
        # Generate response using the generative model with the structured prompt
        feedback = model.generate_content(prompt).text
        return f"{feedback}"

    except Exception as e:
        print("Error:", str(e))
        return "Sorry, something went wrong. Please try again later."

@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    survey_data = request.json
    mood_score = sum(survey_data.values())
    feedback = generate_feedback(survey_data, mood_score)
    return jsonify({'mood_score': mood_score, 'feedback': feedback})

if __name__ == '__main__':
    app.run(debug=True)