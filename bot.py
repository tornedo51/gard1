import discord
from discord.ext import commands
import sqlite3
from dotenv import load_dotenv
import os

# تحميل المتغيرات من ملف .env
load_dotenv()

intents = discord.Intents.all()
intents.messages = True
bot = commands.Bot(command_prefix='$', intents=intents)

# معرف الروم المحدد
TARGET_CHANNEL_ID = 123456789012345678  # استبدل هذا بالمعرف الحقيقي للروم

# الاتصال بقاعدة البيانات وإنشاء الجدول إذا لم يكن موجودًا
conn = sqlite3.connect('message_counts.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS message_counts (
        user_id INTEGER PRIMARY KEY,
        user_name TEXT,
        count INTEGER
    )
''')
conn.commit()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # التحقق من أن الرسالة في الروم المحدد
    if message.channel.id == 1240812609268224091:
        user_id = message.author.id
        user_name = message.author.name

        # تحديث عدد الرسائل في قاعدة البيانات
        c.execute('SELECT count FROM message_counts WHERE user_id = ?', (user_id,))
        result = c.fetchone()

        if result:
            new_count = result[0] + 1
            c.execute('UPDATE message_counts SET count = ? WHERE user_id = ?', (new_count, user_id))
        else:
            c.execute('INSERT INTO message_counts (user_id, user_name, count) VALUES (?, ?, ?)', (user_id, user_name, 1))
        
        conn.commit()
    
    await bot.process_commands(message)

@bot.command()
async def stats(ctx):
    # قراءة البيانات من قاعدة البيانات وإنشاء رسالة تحتوي على عدد الرسائل لكل مستخدم
    c.execute('SELECT user_name, count FROM message_counts')
    rows = c.fetchall()

    stats_message = "Message count per user:\n"
    for row in rows:
        stats_message += f"{row[0]}: {row[1]} messages\n"
    
    await ctx.send(stats_message)

@bot.command()
@commands.has_permissions(administrator=True)  # يتطلب أن يكون للمستخدم صلاحيات المدير
async def reset_stats(ctx):
    # تصفير البيانات في قاعدة البيانات
    c.execute('DELETE FROM message_counts')
    conn.commit()
    await ctx.send("Message counts have been reset.")

# الحصول على التوكن من ملف .env
TOKEN = os.getenv('DISCORD_TOKEN')

# تشغيل البوت
bot.run(TOKEN)
