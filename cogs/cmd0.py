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

# 定義名為 Main 的 Cog
class Main(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 設定歡迎頻道的指令
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_welcome(self, ctx, channel: discord.TextChannel):
        data = loadjson()
        guild_id = str(ctx.guild.id)
        # 初始化伺服器資料
        if guild_id not in data:
            data[guild_id] = {}
        data[guild_id]["welcome_channel"] = channel.id  # 儲存伺服器的歡迎頻道 ID
        savejson(data)
        await send_embed_message(ctx, f"已成功設定歡迎頻道為 {channel.mention}", discord.Color.green())

    # 當成員加入時觸發的事件
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        data = loadjson()
        guild_id = str(member.guild.id)
        channel_id = data.get(guild_id, {}).get("welcome_channel")  # 取得伺服器的歡迎頻道 ID
        if channel_id:  # 檢查是否有設定歡迎頻道
            channel = member.guild.get_channel(channel_id)
            if channel:
                # 假設每個伺服器的隊伍顏色已經儲存在設定檔中
                team_color = data.get(guild_id, {}).get("team_color", 0x00FF00)  # 預設顏色為綠色
                embed = discord.Embed(
                    title=f"歡迎 {member.name}",
                    description=f"{member.mention} 加入 {member.guild.name}!",
                    color=discord.Color(team_color)
                )
                embed.set_thumbnail(url=member.avatar.url)  # 添加使用者的頭像
                await channel.send(embed=embed)

    # 設定離開頻道的指令
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_left(self, ctx, channel: discord.TextChannel):
        data = loadjson()
        guild_id = str(ctx.guild.id)
        # 初始化伺服器資料
        if guild_id not in data:
            data[guild_id] = {}
        data[guild_id]["left_channel"] = channel.id  # 儲存伺服器的離開頻道 ID
        savejson(data)
        await send_embed_message(ctx, f"已成功設定離開頻道為 {channel.mention}", discord.Color.green())

    # 當成員離開時觸發的事件
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        data = loadjson()
        guild_id = str(member.guild.id)
        channel_id = data.get(guild_id, {}).get("left_channel")  # 取得伺服器的離開頻道 ID
        if channel_id:  # 檢查是否有設定離開頻道
            channel = member.guild.get_channel(channel_id)
            if channel:
                # 假設每個伺服器的隊伍顏色已經儲存在設定檔中
                team_color = data.get(guild_id, {}).get("team_color", 0xFF0000)  # 預設顏色為紅色
                embed = discord.Embed(
                    title=f"再見 {member.name}",
                    description=f"很遺憾 {member.mention} 離開 {member.guild.name}!",
                    color=discord.Color(team_color)
                )
                embed.set_thumbnail(url=member.avatar.url)  # 添加使用者的頭像
                await channel.send(embed=embed)

    # 設定隊伍顏色的指令
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_team_color(self, ctx, color: str):
        data = loadjson()
        guild_id = str(ctx.guild.id)
        # 檢查顏色格式是否正確
        try:
            team_color = int(color, 16)  # 將顏色代碼轉為整數
            if guild_id not in data:
                data[guild_id] = {}
            data[guild_id]["team_color"] = team_color  # 儲存隊伍顏色
            savejson(data)
            await send_embed_message(ctx, f"已成功設定隊伍顏色為 #{color}", discord.Color(team_color))
        except ValueError:
            await send_embed_message(ctx, "顏色格式錯誤，請輸入有效的十六進位顏色代碼（例如：FF5733）。", discord.Color.red())

# 在啟動時將 bot 註冊進該 cog
async def setup(bot):
    await bot.add_cog(Main(bot))
