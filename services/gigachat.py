import os
from gigachat import GigaChat
from dotenv import load_dotenv
import json
from gigachat.models import Chat, Messages
from datetime import datetime

load_dotenv()

giga = GigaChat(
    credentials=os.getenv("GIGACHAT_AUTH"),
    verify_ssl_certs=False,
    model="GigaChat-Pro"
)

with open("prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read().strip()

async def safe_ask_gigachat(schedule: str, question: str, history: list[Messages]) -> str:
    current_time_str = datetime.now().strftime("%A, %d %B %Y, %H:%M")
    user_prompt = f"Текущее время: {current_time_str}\n\nРасписание:\n{schedule}\n\nВопрос: {question}"

    # Формируем полный список сообщений: системный промпт + история + новый вопрос
    all_messages = [Messages(role="system", content=SYSTEM_PROMPT)] + history + [Messages(role="user", content=user_prompt)]

    payload = Chat(
        messages=all_messages,
        temperature=0.7 # Добавим немного "творчества" для более живых ответов
    )
    res = await giga.achat(payload)
    return res.choices[0].message.content

async def get_schedule_from_text(schedule_text: str) -> dict | None:
    prompt = (
        "Преобразуй это текстовое расписание в JSON. "
        "Ключами верхнего уровня должны быть дни недели на русском языке с заглавной буквы (например, 'Понедельник'). "
        "Значениями должен быть список объектов, где каждый объект - это урок со следующими ключами: 'start_time' (HH:MM), 'end_time' (HH:MM), 'subject' (название предмета), 'cabinet' (номер кабинета или 'Н/У'). "
        "Если время или кабинет не указаны, не добавляй эти ключи. "
        "Не добавляй ничего, кроме JSON.\n\n"
        f"Расписание:\n{schedule_text}"
    )
    payload = Chat(
        messages=[Messages(role="user", content=prompt)],
        temperature=0.1
    )
    try:
        response = await giga.achat(payload)
        json_text = response.choices[0].message.content.strip()
        # Иногда модель оборачивает JSON в ```json ... ```
        json_text = json_text.replace("```json", "").replace("```", "").strip()
        return json.loads(json_text)
    except (json.JSONDecodeError, IndexError) as e:
        return None

async def is_schedule_update_statement(text: str) -> bool:
    prompt = (
        "Проанализируй следующее сообщение. Является ли оно утверждением о временном изменении в расписании "
        "(например, отмена урока, замена одного предмета другим, изменение кабинета на один день)? "
        "Примеры таких утверждений: 'Завтра не будет физики', 'Вместо истории будет математика', 'Первый урок отменили', 'Географию перенесли в 301'.\n"
        "Примеры сообщений, которые НЕ являются утверждениями: 'Какое расписание на завтра?', 'Где будет физика?'.\n\n"
        f"Сообщение: \"{text}\"\n\n"
        "Ответь только одно слово: 'Да' или 'Нет'."
    )
    payload = Chat(messages=[Messages(role="user", content=prompt)], temperature=0.1)
    try:
        response = await giga.achat(payload)
        answer = response.choices[0].message.content.strip().lower()
        return "да" in answer
    except Exception:
        return False

async def get_tomorrow_summary(schedule: str) -> str:
    question = (
        "Ты — заботливый помощник, который помогает не выгореть. "
        "На основе этого расписания сделай краткую сводку на завтра. "
        "Оцени сложность дня (легкий, средний, трудный). "
        "Если день легкий, обязательно напиши что-то ободряющее, например: «У тебя завтра несложный день, можешь отдохнуть лишний раз!». "
        "Если день трудный, дай небольшой совет, как с ним справиться, например: «Завтра будет насыщенно, не забудь хорошо отдохнуть сегодня». "
        "Будь краток, дружелюбен и используй смайлики."
    )
    return await safe_ask_gigachat(schedule, question, [])