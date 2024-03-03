from flask import Flask, request, jsonify

app = Flask(__name__)

# This is a placeholder for your session data
sessions = {
    "sess1": {
        "questions": [
            {
                "question_text": "What is the capital of France?",
                "example_sentence": "Paris is the capital of France.",
                "question_type": "READ"
            },
            {
                "question_text": "What is 2 + 2?",
                "example_sentence": "If you have 2 apples and you buy 2 more, you have 4 apples.",
                "question_type": "WRITE"
            },
            {
                "question_text": "What does 'happy' mean?",
                "example_sentence": "I feel happy when I spend time with my friends.",
                "question_type": "MEANING"
            }
        ]
    }
}

@app.route('/api/nextQ', methods=['GET'])
def next_question():
    session_id = request.args.get('sessionId')
    
    if session_id not in sessions:
        return jsonify({"error": "Invalid session ID"}), 400
    
    session_data = sessions[session_id]
    questions = session_data.get('questions', [])
    
    # For simplicity, just return the first question
    if questions:
        return jsonify(questions[0])
    else:
        return jsonify({"message": "No more questions in this session"})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")