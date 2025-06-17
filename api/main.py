from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bot.handlers import User, model_handler, generate_random_data, predict_heart_attack

app = FastAPI()

# хранилище пользователей
users = {}


# модель данных для создания пользователя
class UserCreate(BaseModel):
    id: int
    gender: str
    age: int
    sugar_level: float
    ck_mb: float


# модель данных для обновления пользователя
class UserUpdate(BaseModel):
    gender: str
    age: int
    sugar_level: float
    ck_mb: float


@app.post("/users/", response_model=dict)
def create_user(user: UserCreate):
    if user.id in users:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    users[user.id] = User(user.id, user.gender, user.age, user.sugar_level, user.ck_mb)
    return {"message": "Пользователь был успешно создан"}


@app.get("/users/{user_id}", response_model=dict)
def get_user(user_id: int):
    user = users.get(user_id)
    if user:
        return user.__dict__
    raise HTTPException(status_code=404, detail="Пользователь не найден")


@app.put("/users/{user_id}", response_model=dict)
def update_user(user_id: int, user_update: UserUpdate):
    user = users.get(user_id)
    if user:
        user.update_gender(user_update.gender)
        user.update_age(user_update.age)
        user.update_sugar_level(user_update.sugar_level)
        user.update_ck_mb(user_update.ck_mb)
        return {"message": "Пользователь успешно обновлен"}
    raise HTTPException(status_code=404, detail="Пользователь не найден")


@app.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int):
    if user_id in users:
        del users[user_id]
        return {"message": "Пользователь успешно удален"}
    raise HTTPException(status_code=404, detail="Пользователь не найден")


@app.post("/predict/", response_model=dict)
def predict(user_id: int):
    user = users.get(user_id)
    if user:
        random_data = generate_random_data()
        risk = predict_heart_attack(model_handler, user, random_data)
        return {"risk": risk}
    raise HTTPException(status_code=404, detail="Пользователь не найден")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
