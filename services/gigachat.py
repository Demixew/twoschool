import os
from gigachat import GigaChat
from dotenv import load_dotenv
from gigachat.models import Chat, Messages

load_dotenv()

giga = GigaChat(
    credentials=os.getenv("GIGACHAT_AUTH"),
    verify_ssl_certs=False,
    model="GigaChat-Pro"
)

async def safe_ask_gigachat(schedule: str, question: str) -> str:
    system_prompt = (
        "Ты — дружелюбный школьный ассистент. Твоя задача — помогать с расписанием. "
        "Вся информация для ответа находится в тексте расписания, который я тебе предоставлю. "
        "Никогда не придумывай информацию. Если ответа нет в расписании, вежливо сообщи об этом, "
        "например: «К сожалению, я не нашёл этой информации в расписании». "
        "Твои ответы должны быть краткими и по делу. Обращайся к пользователю на 'ты'."
    )
    user_prompt = f"Расписание:\n{schedule}\n\nВопрос: {question}"
    payload = Chat(
        messages=[
            Messages(role="system", content=system_prompt),
            Messages(role="user", content=user_prompt)
        ]
    )
    res = await giga.achat(payload)
    return res.choices[0].message.content