from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import QuizQuestion, UserResponse
from auth import get_current_user_from_token
from crud import get_user_by_username

templates = Jinja2Templates(directory="templates")
router = APIRouter()

# Sample questions
sample_questions = [
    {
        "question_text": "What is the capital of France?",
        "options": ["London", "Paris", "Berlin", "Madrid"],
        "correct_answer": "Paris",
        "category": "Geography"
    },
    {
        "question_text": "Which planet is known as the Red Planet?",
        "options": ["Venus", "Mars", "Jupiter", "Saturn"],
        "correct_answer": "Mars",
        "category": "Science"
    }
]

@router.get("/quiz", response_class=HTMLResponse)
async def show_quiz(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.cookies.get("token")
        if not token:
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
            
        username = get_current_user_from_token(token)
        user = get_user_by_username(db, username)

        questions = db.query(QuizQuestion).all()
        
        # Populate sample questions if DB is empty
        if not questions:
            for q in sample_questions:
                new_question = QuizQuestion(
                    question_text=q["question_text"],
                    options=q["options"],  # Store as list (JSON)
                    correct_answer=q["correct_answer"],
                    category=q["category"]
                )
                db.add(new_question)
            db.commit()
            questions = db.query(QuizQuestion).all()
        
        return templates.TemplateResponse("quiz.html", {
            "request": request,
            "questions": questions,
            "logged_in": True,
            "username": username
        })

    except Exception as e:
        return RedirectResponse(
            url=f"/login?msg=Error+loading+quiz:+{str(e)}",
            status_code=status.HTTP_302_FOUND
        )


@router.post("/submit-quiz")
async def submit_quiz(
    request: Request,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user_from_token)
):
    form_data = await request.form()
    user = get_user_by_username(db, current_user)
    
    score = 0
    total = 0

    for key, value in form_data.items():
        if key.startswith("question_"):
            total += 1
            question_id = int(key.split("_")[1])
            question = db.query(QuizQuestion).filter_by(id=question_id).first()

            # Avoid duplicate submissions
            existing = db.query(UserResponse).filter_by(
                user_id=user.id, question_id=question_id
            ).first()
            if existing:
                continue

            is_correct = value == question.correct_answer

            response = UserResponse(
                user_id=user.id,
                question_id=question_id,
                selected_answer=value,
                is_correct=is_correct
            )
            db.add(response)

            if is_correct:
                score += 1

    db.commit()

    return templates.TemplateResponse("quiz_results.html", {
        "request": request,
        "score": score,
        "total": total,
        "percentage": (score / total) * 100 if total > 0 else 0,
        "logged_in": True,
        "username": current_user
    })
