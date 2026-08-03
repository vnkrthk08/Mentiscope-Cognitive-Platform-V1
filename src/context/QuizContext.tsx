import React, { createContext, useContext, useState } from "react";

interface QuizContextType {
  quizActive: boolean;
  setQuizActive: (active: boolean) => void;
}

const QuizContext = createContext<QuizContextType>({
  quizActive: false,
  setQuizActive: () => {},
});

export const QuizProvider = ({ children }: { children: React.ReactNode }) => {
  const [quizActive, setQuizActive] = useState(false);
  return (
    <QuizContext.Provider value={{ quizActive, setQuizActive }}>
      {children}
    </QuizContext.Provider>
  );
};

export const useQuiz = () => useContext(QuizContext);
