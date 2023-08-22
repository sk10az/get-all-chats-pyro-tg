import asyncio
import json
import os
import time

from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.errors import FloodWait
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

load_dotenv()

app_id = os.getenv("APP_ID")
api_hash = os.getenv("API_HASH")

# TARGETS: List - список айди каналов
TARGETS = []

engine = create_engine("sqlite:///example.db")  # echo True
Session = sessionmaker(bind=engine)
session = Session()


class Base(DeclarativeBase):
    pass


class User(Base):
    """Модель пользователя"""
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)

    first_name: Mapped[str] = mapped_column(String(100))
    username_name: Mapped[str] = mapped_column(String(100))
    target: Mapped[str] = mapped_column(String(100))

    def __repr__(self) -> str:
        return f"User(id={self.id!r}"  # , name={self.name!r}


Base.metadata.create_all(engine)


async def main() -> None:
    async with Client("", app_id, api_hash) as app:
        try:
            async for dialog in app.get_dialogs():
                """Получения всех чатов и каналов кроме тех, которые относяться к типам бот либо приватный"""
                data = json.loads(str(dialog))
                if data["chat"]["type"] != "ChatType.PRIVATE" and data["chat"]["type"] != "ChatType.BOT":
                    TARGETS.append(dialog.chat.id)
        except:
            ...

        count = 0
        for channel_id in TARGETS:
            async for member in app.get_chat_members(channel_id):
                """Добавить пользователя в базу данных из канала либо чата"""
                try:
                    data = json.loads(str(member))
                    id_value = data['user']['id']
                    first_name_value = data['user']['first_name']
                    username_value = data['user']['username']
                    new_user = User(
                        id=id_value,
                        first_name=first_name_value,
                        username_name=username_value,
                        target=channel_id
                    )
                    session.add(new_user)
                    session.commit()
                    count += 1
                    print(count)

                except FloodWait as e:
                    time.sleep(e.value)
                    continue

                except Exception:
                    continue


if __name__ == '__main__':
    asyncio.run(main())
