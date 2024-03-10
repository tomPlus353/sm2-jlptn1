import React, { useState, useEffect } from 'react';
//import ReactDOM from 'react-dom';
import axios from './axiosConfig';

const App = () => {
  const [currentState, setCurrentState] = useState('intro');
  const [sessionId, setSessionId] = useState('');
  const [numberOfQuestions, setNumberOfQuestions] = useState('');
  const [currentQuestionNumber, setCurrentQuestionNumber] = useState(0);
  const [currentQuestion, setCurrentQuestion] = useState({});
  const [userAnswer, setUserAnswer] = useState('');
  const [feedback, setFeedback] = useState('');
  const [quizEnded, setQuizEnded] = useState(false);
  const [quizScore, setQuizScore] = useState({ correct: 0, total: 0 });

  const handleStartQuiz = async () => {
    const response = await axios.post('/api/startQuiz', { numberOfQuestions });
    setSessionId(response.data.sessionId);
    handleFirstQuestion(response.data.sessionId);
    // setCurrentState('question');
  };

  const handleFirstQuestion = async (nonStateSessionId) => {
    const response = await axios.get(`/api/nextQuestion?sessionId=${nonStateSessionId}`);
    console.log("response to handleNextQuestions: "+ JSON.stringify(response.data))
    setCurrentQuestion(response.data);
    setCurrentQuestionNumber(currentQuestionNumber +1);
    setUserAnswer('');
    setCurrentState('question');
  };

  const handleNextQuestion = async () => {
    const response = await axios.get(`/api/nextQuestion?sessionId=${sessionId}`);
    console.log("response to handleNextQuestions: "+ JSON.stringify(response.data))
    setCurrentQuestion(response.data);
    setCurrentQuestionNumber(currentQuestionNumber +1);
    setUserAnswer('');
    setCurrentState('question');
  };

  const handleSubmitAnswer = async () => {
    console.log("current question is " + JSON.stringify(currentQuestion))
    var question_id = currentQuestion.question_id;
    console.log("question id is " + question_id);
    const response = await axios.post('/api/submitAnswer', {
      sessionId,
      question_id,
      userAnswer,
    });
    setFeedback(response.data.feedback);
    setQuizScore({
      correct: response.data.quizScore.correct,
      total: response.data.quizScore.total,
    });
    if (response.data.quizEnded) {
      setQuizEnded(true);
      setCurrentState('questionFeedback');
    } else {
      setCurrentState('questionFeedback');
    }
  };

  const handleEndQuiz = async () => {
    setCurrentState('sessionFeedback');
  };

  const handlePlayAgain = () => {
    setCurrentState('intro');
    setSessionId('');
    setNumberOfQuestions('');
  };

  useEffect(() => {
    if (currentState === 'intro') {
      setSessionId('');
      setNumberOfQuestions('');
      setCurrentQuestionNumber(0);
      setCurrentQuestion({});
      setQuizEnded(false);
    } else if (currentState === 'question') {
      setUserAnswer('');
      setFeedback('');
    }
  }, [currentState]);

  const renderIntroState = () => (
    <div>
      <h1>Welcome to the Quiz App!</h1>
      <p>Please enter the number of questions you'd like to answer:</p>
      <input
        type="number"
        value={numberOfQuestions}
        onChange={(e) => setNumberOfQuestions(e.target.value)}
      />
      <button onClick={handleStartQuiz}>Start Quiz</button>
    </div>
  );

  const renderQuestionState = function() {
    return <div>
      <h2>Question {currentQuestionNumber}</h2>
      <p>{currentQuestion.question_text}</p>
      <input
        type="text"
        value={userAnswer}
        onChange={(e) => setUserAnswer(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            handleSubmitAnswer();
          }
        }}
      />
      <button onClick={handleSubmitAnswer}>Submit Answer</button>
    </div>
  };

  const renderQuestionFeedbackState = () => (
    <div>
      <p>{feedback}</p>
      <p>Score: {quizScore.correct}/{quizScore.total}</p>
      {quizEnded ? (
        <div>
          <p>Quiz is over!</p>
          <button onClick={handleEndQuiz}>End Quiz</button>
        </div>
      ) : (
        <button onClick={handleNextQuestion}>Next Question</button>
      )}
    </div>
  );

  const renderSessionFeedbackState = () => (
    <div>
      <p>Quiz session feedback:</p>
      <p>Score: {quizScore.correct}/{quizScore.total}</p>
      <p>Percentage: {(quizScore.correct / quizScore.total) * 100}%</p>
      <br/>
      {(quizScore.correct / quizScore.total) * 100 >= 80 ? "😊😊😊" : "😒😒😒"}
      <br/>
      <button onClick={handlePlayAgain}>Play Again</button>
      <br/>
      
    </div>
  );

  let currentStateComponent;
  switch (currentState) {
    case 'intro':
      currentStateComponent = renderIntroState();
      break;
    case 'question':
      currentStateComponent = renderQuestionState();
      break;
    case 'questionFeedback':
      currentStateComponent = renderQuestionFeedbackState();
      break;
    case 'sessionFeedback':
      currentStateComponent = renderSessionFeedbackState();
      break;
    default:
      currentStateComponent = renderIntroState();
  }

  return <div>{currentStateComponent}</div>;
};
export default App
// ReactDOM.render(<App />, document.getElementById('root'));
