import discord
from discord.ext import commands
import requests
import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if any('\u3040' <= c <= '\u30FF' or '\u4E00' <= c <= '\u9FFF' for c in message.content):
        translated = translate_to_english(message.content)

        author_name = message.author.display_name
        short_name = author_name[:4]  

        translated_channel = discord.utils.get(message.guild.text_channels, name="translated")
        if translated_channel:
            await translated_channel.send(
                f"【{short_name}】: {message.content}\n⬇\n**{translated}**"
            )
        else:
            print("⚠️ 'translated' チャンネルが見つかりません")

    await bot.process_commands(message)

def translate_to_english(text):
    placeholder_map = {
        "葬送": "__SOUSOU__",
        "ふわあに": "__FUWAHNI__"
    }

    for word, placeholder in placeholder_map.items():
        text = text.replace(word, placeholder)

    url = "https://api-free.deepl.com/v2/translate"
    params = {
        "auth_key": DEEPL_API_KEY,
        "text": text,
        "source_lang": "JA",
        "target_lang": "EN"
    }
    response = requests.post(url, data=params)
    if response.status_code != 200:
        print(f"❌ DeepL API エラー: {response.text}")
        return "[翻訳失敗]"

    translated = response.json()["translations"][0]["text"]

    for word, placeholder in placeholder_map.items():
        translated = translated.replace(placeholder, f"'{word}'")

    return translated

bot.run(DISCORD_TOKEN)
