import discord
from discord.ext import commands
import json
import os
import asyncio
import re

# 設定檔案名稱
setting = "setting.json"
intents = discord.Intents.default()
intents.guilds = True
intents.members = True  # 需要成員加入和離開的事件
intents.messages = True  # 需要處理消息事件

# 檢查 JSON 文件是否存在，否則建立空的
if not os.path.exists(setting):
    with open(setting, "w") as f:
        json.dump({}, f)

# 載入 JSON 文件
def loadjson():
    with open(setting, "r") as f:
        return json.load(f)

# 儲存 JSON 文件
def savejson(data):
    with open(setting, "w") as f:
        json.dump(data, f, indent=4)

# 發送嵌入訊息
async def send_embed_message(ctx, content, color=discord.Color.blue()):
    embed = discord.Embed(
        description=content,
        color=color  # 設定訊息的顏色
    )
    await ctx.send(embed=embed)

def parse_time(time_str):
    time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400, "y": 31536000}
    match = re.match(r"(\d+)([smhdy])", time_str)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        return amount * time_units[unit]
    else:
        return None

# 定義名為 Main 的 Cog
class cmd(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 前綴指令
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: str, *, reason=None):
        mute_duration = parse_time(duration)
        if mute_duration is None:
            await send_embed_message(ctx, "請提供有效的時間格式！格式為: `<數字><單位>` (s, m, h, d, y)", discord.Color.red())
            return

        data = loadjson()
        guild_id = str(ctx.guild.id)
        
        # 檢查是否已有禁音角色，若無則創建一個
        mute_role_id = data.get(guild_id, {}).get("mute_role")
        if mute_role_id:
            mute_role = ctx.guild.get_role(mute_role_id)
        else:
            mute_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, speak=False, send_messages=False)
            if guild_id not in data:
                data[guild_id] = {}
            data[guild_id]["mute_role"] = mute_role.id
            savejson(data)

        # 將禁音角色添加到成員
        await member.add_roles(mute_role, reason=reason)
        await send_embed_message(ctx, f"{member.mention} 已被靜音 {duration}，原因: {reason}", discord.Color.red())

        # 在指定時間後自動解除禁音
        await asyncio.sleep(mute_duration)
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
            await send_embed_message(ctx, f"{member.mention} 的靜音時間已到，已自動解除靜音", discord.Color.green())

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        data = loadjson()
        guild_id = str(ctx.guild.id)
        mute_role_id = data.get(guild_id, {}).get("mute_role")

        if mute_role_id:
            mute_role = ctx.guild.get_role(mute_role_id)
            if mute_role in member.roles:
                await member.remove_roles(mute_role)
                await send_embed_message(ctx, f"{member.mention} 已解除靜音", discord.Color.green())
            else:
                await send_embed_message(ctx, f"{member.mention} 不在靜音狀態", discord.Color.yellow())
        else:
            await send_embed_message(ctx, "本伺服器尚未設定禁音角色", discord.Color.orange())

    @commands.command()
    async def Hello(self, ctx: commands.Context):
        await send_embed_message(ctx, "Hello, world!", discord.Color.blue())
        print("Hello")

    # 設定歡迎頻道的指令

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def link(self, ctx):
        """啟用自動刪除所有連結功能"""
        data = loadjson()
        guild_id = str(ctx.guild.id)

        if guild_id not in data:
            data[guild_id] = {}

        data[guild_id]["link_protection"] = True
        savejson(data)
        await send_embed_message(ctx, "已啟用自動刪除所有連結的功能", discord.Color.green())

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unlink(self, ctx):
        """停用自動刪除連結功能"""
        data = loadjson()
        guild_id = str(ctx.guild.id)

        if guild_id in data and "link_protection" in data[guild_id]:
            data[guild_id]["link_protection"] = False
            savejson(data)
            await send_embed_message(ctx, "已停用自動刪除所有連結的功能", discord.Color.green())
        else:
            await send_embed_message(ctx, "自動刪除功能尚未啟用", discord.Color.red())

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        data = loadjson()
        guild_id = str(message.guild.id)
        link_protection = data.get(guild_id, {}).get("link_protection", False)

        # 使用正則表達式檢測所有連結
        url_pattern = re.compile(r"(https?://[^\s]+)")
        if link_protection and url_pattern.search(message.content):
            await message.delete()
            try:
                await message.author.send("您的訊息包含不允許的連結，請勿在伺服器中發送連結。")
            except discord.Forbidden:
                print(f"無法向 {message.author} 傳送私訊")

# 在啟動時將 bot 註冊進該 cog
async def setup(bot):
    await bot.add_cog(cmd(bot))
