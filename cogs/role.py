import discord
from discord.ext import commands
import json
import os

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

# 定義名為 role 的 Cog
class role(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """當成員加入伺服器時，自動給予指定的角色"""
        data = loadjson()
        guild_id = str(member.guild.id)
        if guild_id in data and "auto_role" in data[guild_id]:
            role_id = data[guild_id]["auto_role"]
            role = discord.utils.get(member.guild.roles, id=int(role_id))
            if role:
                await member.add_roles(role)
                await send_embed_message(member.guild, f"{member.mention} 已自動獲得角色: {role.name}")
            else:
                print(f"角色 ID {role_id} 找不到，請檢查設定檔案。")
        else:
            print(f"伺服器 {guild_id} 沒有設定 auto_role。")

    # 設定 AutoRole 角色
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setautorole(self, ctx, role: discord.Role):
        """設定自動加入的角色"""
        data = loadjson()
        guild_id = str(ctx.guild.id)
        if guild_id not in data:
            data[guild_id] = {}
        data[guild_id]["auto_role"] = str(role.id)
        savejson(data)
        await send_embed_message(ctx, f"自動加入的角色已設定為: {role.name}", discord.Color.green())

    # 查看當前的 AutoRole 設置
    @commands.command()
    async def currentautorole(self, ctx):
        """查看當前設定的自動角色"""
        data = loadjson()
        guild_id = str(ctx.guild.id)
        if guild_id in data and "auto_role" in data[guild_id]:
            role_id = data[guild_id]["auto_role"]
            role = discord.utils.get(ctx.guild.roles, id=int(role_id))
            if role:
                await send_embed_message(ctx, f"當前的自動角色為: {role.name}", discord.Color.green())
            else:
                await send_embed_message(ctx, "找不到設定的自動角色，請檢查設定檔案。", discord.Color.red())
        else:
            await send_embed_message(ctx, "此伺服器尚未設置自動角色。", discord.Color.red())

# 在啟動時將 bot 註冊進該 cog
async def setup(bot):
    await bot.add_cog(role(bot))
