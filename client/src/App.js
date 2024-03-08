import React, { useState, useEffect } from 'react';
//import ReactDOM from 'react-dom';
import axios from './axiosConfig';

const App = () => {
  const [currentState, setCurrentState] = useState('intro');
  const [sessionId, setSessionId] = useState('');
  const [numberOfQuestions, setNumberOfQuestions] = useState('');
  const [currentQuestion, setCurrentQuestion] = useState({});
  const [userAnswer, setUserAnswer] = useState('');
  const [feedback, setFeedback] = useState('');
  const [quizEnded, setQuizEnded] = useState(false);
  const [quizScore, setQuizScore] = useState({ correct: 0, total: 0 });

  const handleStartQuiz = async () => {
    const response = await axios.post('/api/startQuiz', { numberOfQuestions });
    setSessionId(response.data.sessionId);
    setCurrentState('question');
  };

  const handleNextQuestion = async () => {
    const response = await axios.get(`/api/nextQuestion?sessionId=${sessionId}`);
    setCurrentQuestion(response.data);
    setUserAnswer('');
    setCurrentState('question');
  };

  const handleSubmitAnswer = async () => {
    const response = await axios.post('/api/submitAnswer', {
      sessionId,
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

  useEffect(() => {
    if (currentState === 'intro') {
      setSessionId('');
      setNumberOfQuestions('');
    } else if (currentState === 'question') {
      setCurrentQuestion({});
      setUserAnswer('');
      setFeedback('');
      setQuizEnded(false);
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

  const renderQuestionState = () => (
    <div>
      <h2>Question {quizScore.total + 1}</h2>
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
  );

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
      {/* You can add UI elements or emojis to indicate performance */}
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
