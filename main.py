import discord
from discord.ext import tasks, commands
from PIL import Image, ImageDraw, ImageFont
import io
import os

from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Я жив!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()







# Настройка intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.voice_states = True

# Инициализация бота
bot = commands.Bot(command_prefix="!", intents=intents)

# ID сервера (замените на ваш)
GUILD_ID = 1387552821175390339  # Например, 123456789012345678
# Путь к шаблону баннера и шрифту
BANNER_TEMPLATE = "miracle_banner.png"  # Ваше изображение
FONT_PATH = "Roboto-Bold.ttf"  # Жирный шрифт (замените на доступный TTF, например, Roboto-Bold.ttf)


# Настройки шрифта и позиционирования
FONT_SIZE = 70  # Начальный размер шрифта
TEXT_OFFSET_X = 130  # Горизонтальный отступ
TEXT_OFFSET_Y = 380  # Базовый вертикальный отступ
LINE_SPACING = 190  # Расстояние между строками текста
TEXT_COLOR = (0,0,0)  # Цвет шрифта (RGB: розовый)
EXCLUDED_ROLE_IDS = [1388620087551983848, 1389856327907672124]  # Список ID ролей для исключения

@bot.event
async def on_ready():
    print(f"Бот {bot.user.name} готов!")
    update_banner.start()

@tasks.loop(seconds=5)  # Обновление каждые 5 минут
async def update_banner():
    try:
        guild = bot.get_guild(GUILD_ID)
        if not guild:
            print("Ошибка: сервер не найден!")
            return

        # Подсчёт участников с учётом исключения ролей
        total_members = sum(1 for member in guild.members if not any(role.id in EXCLUDED_ROLE_IDS for role in member.roles))
        voice_members = sum(1 for channel in guild.voice_channels for member in channel.members 
                           if not any(role.id in EXCLUDED_ROLE_IDS for role in member.roles))

        # Создание изображения
        image = Image.open(BANNER_TEMPLATE)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        # Добавление текста без центрирования по высоте
        # Текст для участников
        text1 = f"{total_members}"
        text1_bbox = draw.textbbox((0, 0), text1, font=font)
        text1_width = text1_bbox[2] - text1_bbox[0]
        draw.text((TEXT_OFFSET_X + (300 - text1_width) // 2, TEXT_OFFSET_Y), text1, fill=TEXT_COLOR, font=font)

        # Текст для голосовых каналов
        text2 = f"{voice_members}"
        text2_bbox = draw.textbbox((0, 0), text2, font=font)
        text2_width = text2_bbox[2] - text2_bbox[0]
        draw.text((TEXT_OFFSET_X + (300 - text2_width) // 2, TEXT_OFFSET_Y + LINE_SPACING), text2, fill=TEXT_COLOR, font=font)

        # Сохранение изображения в байты
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        # Обновление баннера
        await guild.edit(banner=buffer.read())
        print(f"Баннер обновлён: {total_members} участников, {voice_members} в голосовых")
        buffer.close()

    except Exception as e:
        print(f"Ошибка при обновлении баннера: {e}")


keep_alive()
# Запуск бота
bot.run(os.environ["TOKEN"])