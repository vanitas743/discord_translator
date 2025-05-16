import discord #test
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["ekgames"]
collection = db["notified_links"]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')
    check_announcements.start() 

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    author_name = message.author.display_name
    short_name = author_name[:4]

    translated_channel = discord.utils.get(message.guild.text_channels, name="translated")
    if not translated_channel:
        print("⚠️ 'translated' チャンネルが見つかりません")
        return

    content = message.content
    channel_name = message.channel.name

    if channel_name == "english":
        translated = translate(text=content, source_lang="EN", target_lang="JA")
        await translated_channel.send(
            f"【{short_name}】: {content}\n⬇\n**{translated}**"
        )
    
    elif any('\u3040' <= c <= '\u30FF' or '\u4E00' <= c <= '\u9FFF' for c in content):
        translated = translate(text=content, source_lang="JA", target_lang="EN")
        await translated_channel.send(
            f"【{short_name}】: {content}\n⬇\n**{translated}**"
        )

    await bot.process_commands(message)

def translate(text, source_lang, target_lang):
    # keep Japanese after translate
    placeholder_map = {
        "葬送": "__SOUSOU__",
        "ふわあに": "[[FUWAHNI]]",
        "暇さん": "[[himasan]]",
        "ただ暇な人":"[[tadahimanahito]]",
        "だいず専務": "[[WORD20250516_001]]",
        "専務": "[[WORD20250516_002]]",
        "ラスアタ": "[[LASTATK]]",
        "1鯖": "[[WORD20250516_003]]",
        "2鯖": "[[WORD20250516_004]]"
    }
    # translate to any English words you want from Japanese
    placeholder_map2 = {
        "ラスアタ": "snipe",
        "1鯖": "Server 1",
        "2鯖": "Server 2"
    }

    for word, placeholder in placeholder_map.items():
        text = text.replace(word, placeholder)

    url = "https://api-free.deepl.com/v2/translate"
    params = {
        "auth_key": DEEPL_API_KEY,
        "text": text,
        "source_lang": source_lang,
        "target_lang": target_lang
    }
    response = requests.post(url, data=params)
    if response.status_code != 200:
        print(f"❌ DeepL API エラー: {response.text}")
        return "[翻訳失敗]"

    translated = response.json()["translations"][0]["text"]

    for word, placeholder in placeholder_map.items():
        translated = translated.replace(placeholder, f"'{word}'")
    
    for word, placeholder in placeholder_map2.items():
        translated = translated.replace(f"'{word}'", placeholder)

    return translated
    
@tasks.loop(minutes=5)
async def check_announcements():
    global last_seen_link

    url = "https://announcement.ekgamesserver.com/?ppk=42f47521-f47a-496b-9e90-af01f0f10c37&l=ja"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        a_tags = soup.select("table.table a")
        if len(a_tags) < 2:
            return
        second_a_tag = a_tags[1]

        title = second_a_tag.text.strip()
        href = second_a_tag["href"]
        full_url = f"https://announcement.ekgamesserver.com{href}"

        if "ボーナスクーポン" in title:
            if collection.find_one({"url": full_url}):
                return
            collection.insert_one({"url": full_url})

            coupon_channel = discord.utils.get(bot.get_all_channels(), name="coupon")
            if coupon_channel:
                await coupon_channel.send(f" {title}\n{full_url}")

    except Exception as e:
        print(f"⚠️ クーポン通知エラー: {e}")
bot.run(DISCORD_TOKEN)
