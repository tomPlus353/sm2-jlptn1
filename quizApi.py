from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import utils.cards as cardUtils 
import traceback
from uuid import uuid4

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

    #generate session info
    data = request.json
    number_of_questions = int(data.get('numberOfQuestions', 0))
    session_id =  str(uuid4())  # You can generate a unique session ID here

    #Get active cards
    cardsCollection = cardUtils.getActiveCardsCollection(number_of_questions)
    cardUtils.printCardsDict(cardsCollection)
    session = cardUtils.convertActiveCardsToSession(cardsCollection)
    sessions[session_id] = session
    return jsonify({"sessionId": session_id})

@app.route('/api/nextQuestion', methods=['GET'])
def next_question():
    session_id = request.args.get('sessionId')
    print("session id from client is: ",session_id)
    session = sessions.get(session_id)
    if not session:
        return jsonify({"error": "Invalid session ID"}), 400
    
    questions = session.get('questions', [])
    current_question_index = session.get('current_question_index', 0)
    print("current_question_index: ",current_question_index)
    if current_question_index == len(questions):
        return jsonify({"message": "Error. No more questions in this session"}), 200
    
    current_question = questions[current_question_index]
    
    #increment current question index for the next time
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
    
    # Check if answer is correct
    isCorrect = user_answer == actual_answer;
    if isCorrect:
        quiz_score['correct'] += 1;
    try:
        cardId = questions[current_question_index-1]["question_id"]
        cardUtils.saveCardAnswer(cardId, isCorrect) #save current answer as either correct or incorrect to update smtwo due date
        answerDetails = cardUtils.getAnswerDetails(cardId)
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": "Error when saving result to the DB", "trace": traceback.format_exc() }), 500

    # Check if quiz ended(check if the last Q was that final Q)
    if current_question_index == quiz_score['total']:
        session['quiz_ended'] = True
    
    if isCorrect:
        return jsonify({
            "feedback": "Your answer is correct!",
            "answer": answerDetails,
            "quizScore": quiz_score,
            "quizEnded": session['quiz_ended']
        })
    else:
        return jsonify({
            "feedback": "Your answer is wrong!",
            "answer": answerDetails,
            "quizScore": quiz_score,
            "quizEnded": session['quiz_ended']
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
