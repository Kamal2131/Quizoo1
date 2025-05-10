from sqlalchemy import Column, Integer, String, Boolean, ForeignKey,JSON,DateTime,  UniqueConstraint
from database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, nullable=False)
    options = Column(JSON)  # Store as JSON string
    correct_answer = Column(String)
    category = Column(String)

class UserResponse(Base):
    __tablename__ = "user_responses"
    
    __table_args__ = (UniqueConstraint('user_id', 'question_id', name='uq_user_question'),)
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(Integer, ForeignKey("quiz_questions.id"))
    selected_answer = Column(String)
    is_correct = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())