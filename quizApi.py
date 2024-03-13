from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

"""
Static routes
"""
@app.route('/')
def index():
    return send_from_directory('.','index.html')

"""
API routes
"""
# This is a placeholder for session data
sessions = dict()

@app.route('/api/startQuiz', methods=['POST'])
def start_quiz():
    data = request.json
    number_of_questions = int(data.get('numberOfQuestions', 0))
    session_id = 'session1'  # You can generate a unique session ID here
    sessions[session_id] = {
        'questions': [],
        'current_question_index': 1,
        'quiz_score': {'correct': 0, 'total': number_of_questions},
        'quiz_ended': False
    }
    # Create session with questions
    for i in range(1,1+number_of_questions):
        # Here, you should fetch questions from your question database or API
        question = {
            "question_id": i,
            "question_text": f"Question {i}?",
            "example_sentence": f"Example sentence for question {i}.",
            "answer": f"{i}",
            "question_type": "WRITE"  # Assuming all questions are of WRITE type for simplicity
        }
        sessions[session_id]['questions'].append(question)
    # return jsonify(sessions[session_id])
    return jsonify({"sessionId": session_id})

@app.route('/api/nextQuestion', methods=['GET'])
def next_question():
    session_id = request.args.get('sessionId')
    session = sessions.get(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 400
    
    questions = session.get('questions', [])
    current_question_index = session.get('current_question_index', 0)
    print("current_question_index: ",current_question_index)
    if current_question_index > len(questions):
        return jsonify({"message": "No more questions in this session"}), 200
    
    current_question = questions[current_question_index-1]
    session['current_question_index'] += 1
    
    return jsonify(current_question)

@app.route('/api/submitAnswer', methods=['POST'])
def submit_answer():
    data = request.json;
    print("data object from request to submit_answer", data)
    session_id = data.get('sessionId')
    user_answer = data.get('userAnswer')
    
    session = sessions.get(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 400
    
    current_question_index = session.get('current_question_index', 0)
    quiz_score = session.get('quiz_score', {'correct': 0, 'total': 0})
    questions = session.get('questions', [])
    filteredArray = [v for i,v in enumerate(questions) if questions[i]["question_id"] == data["question_id"]];
    actual_answer = filteredArray[0]["answer"];
    ##current_question = questions[current_question_index - 1]
    
    # Check if answer is correct
    isCorrect = user_answer == actual_answer;
    if isCorrect:
        quiz_score['correct'] += 1;
    
    # Check if quiz ended
    if current_question_index > quiz_score['total']:
        session['quiz_ended'] = True
    
    if isCorrect:
        return jsonify({
            "feedback": "Your answer is correct!",
            "quizScore": quiz_score,
            "quizEnded": session['quiz_ended']
        })
    else:
        return jsonify({
            "feedback": "Your answer is wrong!",
            "quizScore": quiz_score,
            "quizEnded": session['quiz_ended']
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
