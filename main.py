import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
last_seen_link = None

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
    placeholder_map = {
        "葬送": "__SOUSOU__",
        "ふわあに": "[[FUWAHNI]]",
        "暇さん": "[[himasan]]",
        "ただ暇な人":"[[tadahimanahito]]",
        "ラスアタ": "[[LASTATK]]"
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
        if word == "ラスアタ":
            translated = translated.replace(placeholder, "snipe")
        else:
            translated = translated.replace(placeholder, f"'{word}'")

    return translated
    
@tasks.loop(minutes=5)
async def check_announcements():
    global last_seen_link

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

        if "ボーナスクーポン" in title and href != last_seen_link:
            last_seen_link = href
            coupon_channel = discord.utils.get(bot.get_all_channels(), name="coupon")
            if coupon_channel:
                full_url = f"https://announcement.ekgamesserver.com{href}"
                await coupon_channel.send(f"[coupon inc] {title}\n{full_url}")

    except Exception as e:
        print(f"⚠️ クーポン通知エラー: {e}")
bot.run(DISCORD_TOKEN)
