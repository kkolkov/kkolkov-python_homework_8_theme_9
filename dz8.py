from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, field_validator
from datetime import date
import json
import re
from pathlib import Path

app = FastAPI(title="Сервис сбора обращений абонентов")

DATA_FILE = Path("abonents.json")


class Abonent(BaseModel):
    фамилия: str
    имя: str
    дата_рождения: date
    телефон: str
    email: EmailStr

    # Проверка имени и фамилии
    @field_validator("фамилия", "имя")
    @classmethod
    def validate_name(cls, value: str, info):
        if not re.fullmatch(r"[А-ЯЁ][а-яё]+", value):
            raise ValueError(f"{info.field_name.capitalize()} должна начинаться с заглавной буквы и содержать только кириллицу")
        return value

    # Проверка телефона
    @field_validator("телефон")
    @classmethod
    def validate_phone(cls, value: str):
        pattern = r"^\+7\d{10}$"
        if not re.fullmatch(pattern, value):
            raise ValueError("Телефон должен быть в формате +7XXXXXXXXXX (11 цифр после +7)")
        return value


@app.post("/abonent")
def create_abonent(data: Abonent):
    try:
        abonent_data = data.model_dump()
        if DATA_FILE.exists():
            existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        else:
            existing = []

        existing.append(abonent_data)
        DATA_FILE.write_text(json.dumps(existing, ensure_ascii=False, indent=4), encoding="utf-8")

        return {"message": "Обращение успешно сохранено", "abonent": abonent_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
