import discord 
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import os
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

def run_server():
    app.run(host="0.0.0.0", port=8000)

threading.Thread(target=run_server).start()


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
    await bot.tree.sync()
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
    url = "https://announcement.ekgamesserver.com/?ppk=42f47521-f47a-496b-9e90-af01f0f10c37&l=ja"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        first_a_tag = soup.select_one("table.table a")
        if not first_a_tag:
            return

        title = first_a_tag.text.strip()
        href = first_a_tag["href"]
        full_url = f"https://announcement.ekgamesserver.com{href}"

        if "ボーナスクーポン" in title:
            if collection.find_one({"title": title}): 
                return
            collection.insert_one({"title": title})  

            for guild in bot.guilds:
                coupon_channel = discord.utils.get(guild.text_channels, name="coupon")
                if coupon_channel:
                    await coupon_channel.send(f"{title}\n{full_url}")

    except Exception as e:
        print(f"⚠️ クーポン通知エラー: {e}")
        
@bot.tree.command(name="help_links", description="お役立ちリンク集を表示します")
async def help_links(interaction: discord.Interaction):
    await interaction.response.defer()
    message = (
        "📚 **お役立ちリンク集**\n\n"
        "🔗 [装備覚醒効率(awakening efficiency)](https://docs.google.com/spreadsheets/d/1778ykEIFAdwmHKsvD7eO6IZwJJDqwM1aIkb6-1SG3fs/edit?gid=582548854#gid=582548854)\n"
        "📄 [幻想Aの装備利用効率(fantA sword usage)](https://github.com/vanitas743/discord_translator/blob/main/casual_player_path.pdf)\n"
        "📊 [マスタリー効率(mastery)](https://docs.google.com/spreadsheets/d/1tvkYtDlSYwzMNbKAKzib7faO735zEF8lbaB-u7hQWFs/edit?gid=925000323#gid=925000323)\n"
        "💎 [次元の欠片ギア(dimensional shard gear)](https://docs.google.com/spreadsheets/d/1SSxR3do2473shLlToiq-zJzLkjfY7rl-4jkmwtC7aoE/edit?gid=1538649277#gid=1538649277)\n"
        "🌌 [星座(zodiac)](https://docs.google.com/spreadsheets/d/1Zxched7d37tyqGwqLSZYUcTD3dI6QDPyqiPSQ-h-_00/edit?gid=1366379943#gid=1366379943)\n"
        "🐾 [ペット編成(pet optimiser)](https://xanthir.com/fclass/pets/)\n"
        "📰 [お知らせ(info ja)](https://announcement.ekgamesserver.com/?ppk=42f47521-f47a-496b-9e90-af01f0f10c37&l=ja)"
    )
    await interaction.followup.send(message)
    
@bot.tree.command(name="gearawakening", description="装備覚醒効率シートのURLを表示します")
async def gear_awakening(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(
        "🔗 装備覚醒効率(awakening efficiency):\n"
        "https://docs.google.com/spreadsheets/d/1778ykEIFAdwmHKsvD7eO6IZwJJDqwM1aIkb6-1SG3fs/edit?gid=582548854#gid=582548854"
    )

@bot.tree.command(name="fantasword", description="幻想Aの装備利用効率のPDFを表示します")
async def fantasword(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(
        "📄 幻想Aの装備の利用効率(fantA sword usage):\n"
        "https://github.com/vanitas743/discord_translator/blob/main/casual_player_path.pdf"
    )

@bot.tree.command(name="mastery", description="マスタリー効率シートのURLを表示します")
async def mastery(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(
        "📊 マスタリー効率(mastery):\n"
        "https://docs.google.com/spreadsheets/d/1tvkYtDlSYwzMNbKAKzib7faO735zEF8lbaB-u7hQWFs/edit?gid=925000323#gid=925000323"
    )

@bot.tree.command(name="dimshard", description="次元の欠片ギア情報シートのURLを表示します")
async def dimshard(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(
        "💎 次元の欠片ギア(dimensional shard gear):\n"
        "https://docs.google.com/spreadsheets/d/1SSxR3do2473shLlToiq-zJzLkjfY7rl-4jkmwtC7aoE/edit?gid=1538649277#gid=1538649277"
    )

@bot.tree.command(name="zodiac", description="星座(zodiac)情報シートのURLを表示します")
async def zodiac(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(
        "🌌 星座(zodiac):\n"
        "https://docs.google.com/spreadsheets/d/1Zxched7d37tyqGwqLSZYUcTD3dI6QDPyqiPSQ-h-_00/edit?gid=1366379943#gid=1366379943"
    )

@bot.tree.command(name="petoptimizer", description="ペット編成最適化ツールのURLを表示します")
async def petoptimizer(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(
        "🐾 ペット編成(pet optimiser):\n"
        "https://xanthir.com/fclass/pets/"
    )

@bot.tree.command(name="couponinfo", description="お知らせページのURLを表示します")
async def couponinfo(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(
        "📰 お知らせ(info ja):\n"
        "https://announcement.ekgamesserver.com/?ppk=42f47521-f47a-496b-9e90-af01f0f10c37&l=ja"
    )



bot.run(DISCORD_TOKEN)
