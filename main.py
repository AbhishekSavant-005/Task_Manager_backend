from fastapi import FastAPI, HTTPException
from models import user_db, task_db
from schemas import UserCreate, UserRead, TaskCreate, Task, TaskBase

app = FastAPI()

user_counter = 1
task_counter = 1

# ── Users ────────────────────────────────────────────────

@app.post("/users/", response_model=UserRead, status_code=201)
def create_user(user: UserCreate):
    global user_counter
    new_user = UserRead(id=user_counter, **user.model_dump())
    user_db.append(new_user)
    user_counter += 1
    return new_user

@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int):
    for user in user_db:
        if user.id == user_id:
            return user
    raise HTTPException(404, "User not found")

# ── Tasks ────────────────────────────────────────────────

@app.post("/tasks/", response_model=Task, status_code=201)
def create_task(task_in: TaskCreate):
    if not any(u.id == task_in.user_id for u in user_db):
        raise HTTPException(404, "User not found")
    
    global task_counter
    new_task = Task(id=task_counter, **task_in.model_dump())
    task_db.append(new_task)
    task_counter += 1
    return new_task

@app.get("/tasks/", response_model=list[Task])
def list_all_tasks():
    return task_db

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    for t in task_db:
        if t.id == task_id:
            return t
    raise HTTPException(404, "Task not found")

@app.get("/users/{user_id}/tasks", response_model=list[Task])
def get_user_tasks(user_id: int):
    if not any(u.id == user_id for u in user_db):
        raise HTTPException(404, "User not found")
    return [[t,u] for t in task_db for u in user_db if t.user_id == user_id]

@app.put("/tasks/{task_id}", response_model=Task)
def update_task_full(task_id: int, task_in: TaskCreate):
    # Full replace (PUT semantics)
    for i, t in enumerate(task_db):
        if t.id == task_id:
            if not any(u.id == task_in.user_id for u in user_db):
                raise HTTPException(404, "User not found")
            updated = Task(id=task_id, **task_in.model_dump())
            task_db[i] = updated
            return updated
    raise HTTPException(404, "Task not found")

@app.patch("/tasks/{task_id}", response_model=Task)
def update_task_partial(task_id: int, task_update: TaskBase):
    # Partial update (PATCH semantics)
    for t in task_db:
        if t.id == task_id:
            update_data = task_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(t, key, value)
            return t
    raise HTTPException(404, "Task not found")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for i, t in enumerate(task_db):
        if t.id == task_id:
            del task_db[i]
            return {"detail": "Task deleted"}  # or status_code=204
    raise HTTPException(404, "Task not found")