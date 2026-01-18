from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel,Field
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import os

from ai_engine import generate_tutoring_response,generate_quiz
#Load environment variables
load_dotenv()
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

app=FastAPI(
    title="AI Tutoring Service",
    description="An AI-powered tutoring service that provides quizzes and personalized learning experiences.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#Models

class TutoringRequest(BaseModel):
    subject: str = Field(...,example="Mathematics")
    topic: str = Field(...,example="Algebra")
    level:str = Field(...,example="Beginner")    
    question: str = Field(...,example="Can you explain the concept of variables in algebra?")
    learning_style: str= Field("Text-based",example="Understand the concept of variables in algebra")
    preferences: Optional[dict[str,Any]] = Field(None,example={"preferred_format":"text","include_examples":True})
    background_knowledge: Optional[str] = Field(None,example="Basic arithmetic")
    background: Optional[str] = "Beginner"
    language: str = Field("English",example="English")
    
class QuizRequest(BaseModel):
    subject: str = Field(...,example="Mathematics")
    topic: str = Field(...,example="Algebra")
    level: str = Field(...,example="Beginner")
    difficulty: Optional[str] = Field("medium",example="medium")
    language: str = Field("English",example="English")
    num_questions: int = 5


class TutoringResponse(BaseModel):
    response: str

class QuizQuestion(BaseModel):
    quiz:List[Dict[str,Any]]
    formatted_quiz:Optional[str]=None


@app.post("/tutor",response_model=TutoringResponse)
async def get_tutoring_response(data:TutoringRequest):
    try:
        response=generate_tutoring_response(
            subject=data.subject,
            # topic=data.topic,
            level=data.level,
            question=data.question,
            learning_style=data.learning_style,
            # preferences=data.preferences,
            background=data.background,
            language=data.language,
            # api_key=OPENAI_API_KEY
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error generating explanation: {str(e)}")
    
@app.post("/quiz",response_model=QuizQuestion)
async def generate_quiz_api(data:QuizRequest):
    try:

        quiz=generate_quiz(
            subject=data.subject,
            topic=data.topic,
            level=data.level,
            difficulty=data.difficulty,
            language=data.language,
            api_key=OPENAI_API_KEY,
            num_questions=data.num_questions

        )
        # if data.reveal_format:
        #   return{"quiz": quiz,"formatted_quiz":formatted_quiz}
        # else:
        #  return{"quiz": quiz}
        return{"quiz": quiz}
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error generating quiz: {str(e)}")

@app.get("/quiz-html/{subject}/{topic}/{level}/{difficulty}",response_class=HTMLResponse)
async def get_quiz_html(subject:str,topic:str,level:str,difficulty:str):
    try:
        _, formatted_quiz=generate_quiz(
            subject=subject,
            topic=topic,
            level=level,
            difficulty=difficulty,
            language="English",
            api_key=OPENAI_API_KEY
        )
        return HTMLResponse(content=formatted_quiz,status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error generating quiz HTML: {str(e)}")


@app.get("/health")
async def health_check():
        return {"status":"ok"}