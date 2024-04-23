import React, { useState, useEffect } from 'react';
import "./App.css";
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
  const [rightAnswers, setRightAnswers] = useState({ rightEng: "", rightKana: "", rightKanji: "" });


  const handleStartQuiz = async () => {
    const response = await axios.post('/api/startQuiz', { numberOfQuestions });
    setSessionId(response.data.sessionId);
    handleFirstQuestion(response.data.sessionId);
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

  //  {
  //     "rightKanji": card.kanji,
  //     "rightKana": card.kana,
  //     "rightEng": card.defintion
  // }
    setRightAnswers({
      rightKanji: response.data.answer.rightKanji,
      rightKana: response.data.answer.rightKana,
      rightEng: response.data.answer.rightEng,
    });

    //quiz score correct and total
    setQuizScore({
      correct: response.data.quizScore.correct,
      total: response.data.quizScore.total,
    });

    if (response.data.quizEnded) {
      setQuizEnded(true);
    }

     setCurrentState('questionFeedback');
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
    <div className="state-container">
      <h1>Welcome to the Quiz App!</h1>
      <p>Please enter the number of questions you'd like to answer:</p>
      <input
        type="number"
        autoFocus 
        value={numberOfQuestions}
        onChange={(e) => setNumberOfQuestions(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            handleStartQuiz();
          }
        }}
        style={{ marginBottom: '10px' }} // Add margin-bottom to the input

      />
      <button onClick={handleStartQuiz}>Start Quiz</button>
    </div>
  );

  const renderQuestionState = function() {
    return <div className="state-container" >
      <h2>Question {currentQuestionNumber}</h2>
      <p>{currentQuestion.question_text}</p>
      <p>{currentQuestion.example_sentence}</p>
      <input
        type="text"
        autoFocus 
        value={userAnswer}
        onChange={(e) => setUserAnswer(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            handleSubmitAnswer();
          }
        }}
        style={{ marginBottom: '10px' }} // Add margin-bottom to the input
      />
      <button onClick={handleSubmitAnswer}>Submit Answer</button>
    </div>
  };

  const renderQuestionFeedbackState = () => (
    <div className="state-container">
      <p>{feedback}</p>
      <p>{rightAnswers.rightKanji}</p>
      <p>{rightAnswers.rightKana}</p>
      <p>{rightAnswers.rightEng}</p>
      <p>Score: {quizScore.correct}/{quizScore.total}</p>
      {quizEnded ? (
        <div>
          <p>Quiz is over!</p>
          <button autoFocus onClick={handleEndQuiz}>End Quiz</button>
        </div>
      ) : (
        <button autoFocus onClick={handleNextQuestion}>Next Question</button>
      )}
    </div>
  );

  const renderSessionFeedbackState = () => (
    <div className="state-container">
      <p>Quiz session feedback:</p>
      <p>Score: {quizScore.correct}/{quizScore.total}</p>
      <p>Percentage: {(quizScore.correct / quizScore.total) * 100}%</p>
      <p>
      {(quizScore.correct / quizScore.total) * 100 >= 80 ? "😊😊😊" : "😒😒😒"}
      </p>
      <button 
      style={{ marginTop: '16px' }} // Add margin-bottom to the input
      onClick={handlePlayAgain}>Play Again</button>
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
