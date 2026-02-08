from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import engine, SessionLocal, get_db, Base
from models import User, Task
from schemas import UserCreate, UserRead, TaskCreate, TaskRead, TaskBase

app = FastAPI()
Base.metadata.create_all(bind=engine)


# ── Users ────────────────────────────────────────────────

@app.post("/users/", response_model=UserRead, status_code=201)
def create_user(user: UserCreate, db:Session=Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(username=user.username, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ── Tasks ────────────────────────────────────────────────

@app.post("/tasks/", response_model=TaskRead, status_code=201)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == task_in.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found, creating new user.")
    
    db_task = Task(**task_in.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/tasks/", response_model=list[TaskRead])
def list_all_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

@app.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/users/{user_id}/tasks", response_model=list[TaskRead])
def get_user_tasks(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(Task).filter(Task.user_id == user_id).all()

@app.put("/tasks/{task_id}", response_model=TaskRead)
def update_task_full(task_id: int, task_in: TaskCreate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    user = db.query(User).filter(User.id == task_in.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in task_in.model_dump().items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

@app.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task_partial(task_id: int, task_update: TaskBase, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}