import discord
from discord.ext import commands
import json
import os
import re
from discord.ui import Button, View

# 設定檔案名稱
setting = "setting.json"
button_setting = "button_roles.json"
intents = discord.Intents.default()
intents.guilds = True
intents.members = True  # 需要成員加入和離開的事件
intents.messages = True  # 需要處理消息事件

# 檢查 JSON 文件是否存在，否則建立空的
if not os.path.exists(setting):
    with open(setting, "w") as f:
        json.dump({"selfrole": {}}, f)

if not os.path.exists(button_setting):
    with open(button_setting, "w") as f:
        json.dump({"buttons": {}}, f)

# 載入 JSON 文件
def loadjson(filename):
    with open(filename, "r") as f:
        return json.load(f)

# 儲存 JSON 文件
def savejson(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# 發送嵌入訊息
async def send_embed_message(ctx, content, color=discord.Color.blue()):
    embed = discord.Embed(
        description=content,
        color=color
    )
    await ctx.send(embed=embed)

# 定義名為 role 的 Cog
class Role(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # !selfrole @role+<emoji> 指令
    @commands.command()
    async def selfrole(self, ctx, role: str, emoji: str):
        """設定角色和表情符號對應"""
        data = loadjson(setting)

        # 取得當前伺服器 ID
        guild_id = str(ctx.guild.id)

        # 提取角色的 ID
        role_id_match = re.match(r"<@&(\d+)>", role)  # 使用正則表達式解析 @角色
        if role_id_match:
            role_id = role_id_match.group(1)  # 取得角色 ID
        else:
            await send_embed_message(ctx, "Please provide a valid role in the format @Role.", color=discord.Color.red())
            return

        if "selfrole" not in data:
            data["selfrole"] = {}

        # 儲存角色 ID、表情符號和伺服器 ID
        if guild_id not in data["selfrole"]:
            data["selfrole"][guild_id] = {}

        data["selfrole"][guild_id][role_id] = emoji
        savejson(setting, data)

        await send_embed_message(ctx, f"Self Role for role <@&{role_id}> set with emoji {emoji} in this server.")

    # !remove_role @角色 指令
    @commands.command()
    async def remove_role(self, ctx, role: str):
        """刪除角色的紀錄"""
        data = loadjson(setting)

        # 取得當前伺服器 ID
        guild_id = str(ctx.guild.id)

        # 提取角色的 ID
        role_id_match = re.match(r"<@&(\d+)>", role)
        if role_id_match:
            role_id = role_id_match.group(1)
        else:
            await send_embed_message(ctx, "Please provide a valid role in the format @Role.", color=discord.Color.red())
            return

        # 檢查並刪除角色 ID
        if guild_id in data.get("selfrole", {}) and role_id in data["selfrole"][guild_id]:
            del data["selfrole"][guild_id][role_id]
            savejson(setting, data)
            await send_embed_message(ctx, f"Role <@&{role_id}> and its emoji have been removed from this server.")
        else:
            await send_embed_message(ctx, "Role not found in selfrole settings for this server.", color=discord.Color.red())

    # !selfrole_list 指令
    @commands.command()
    async def selfrole_list(self, ctx):
        """顯示所有設置的角色"""
        data = loadjson(setting)

        # 取得當前伺服器 ID
        guild_id = str(ctx.guild.id)
        selfrole_data = data.get("selfrole", {}).get(guild_id, {})

        if not selfrole_data:
            await send_embed_message(ctx, "No self roles set for this server.", color=discord.Color.red())
            return

        # 構建嵌入訊息內容
        description = "\n".join([f"<@&{role_id}>: {emoji}" for role_id, emoji in selfrole_data.items()])
        await send_embed_message(ctx, f"Self Roles for this server:\n{description}", color=discord.Color.green())

    # !runrole 指令
    @commands.command()
    async def runrole(self, ctx, *, text: str):
        """顯示內文並觸發 runselfrole 顯示角色選擇按鈕"""
        if text.strip() == "":
            await send_embed_message(ctx, "Please provide some content after !runrole", color=discord.Color.red())
            return

        # 顯示用戶提供的內文
        await send_embed_message(ctx, text, color=discord.Color.blue())

        # 重新加載自定義角色資料
        data = loadjson(setting)
        button_data = loadjson(button_setting)

        # 取得當前伺服器 ID
        guild_id = str(ctx.guild.id)
        selfrole_data = data.get("selfrole", {}).get(guild_id, {})

        if not selfrole_data:
            await send_embed_message(ctx, "No self roles set for this server.", color=discord.Color.red())
            return

        # 創建 View 並將按鈕加入其中
        view = View()

        # 創建按鈕並設置回調
        for role_id, emoji in selfrole_data.items():
            # 儲存按鈕映射
            if guild_id not in button_data["buttons"]:
                button_data["buttons"][guild_id] = {}

            button_data["buttons"][guild_id][role_id] = emoji
            savejson(button_setting, button_data)

            button = Button(emoji=emoji, style=discord.ButtonStyle.primary)

            # 每次按鈕回調都會重新註冊
            async def button_callback(interaction: discord.Interaction, role_id=role_id):
                member = interaction.user
                role_to_add = discord.utils.get(member.guild.roles, id=int(role_id))
                if role_to_add:
                    # 檢查是否已經擁有這個角色
                    if role_to_add in member.roles:
                        await member.remove_roles(role_to_add)
                        await interaction.response.send_message(f"You have removed the {role_to_add.name} role.", ephemeral=True)
                    else:
                        await member.add_roles(role_to_add)
                        await interaction.response.send_message(f"You have been given the {role_to_add.name} role.", ephemeral=True)
                else:
                    await interaction.response.send_message("Role not found.", ephemeral=True)

            button.callback = button_callback
            view.add_item(button)

        # 發送訊息並附帶按鈕（不使用嵌入內容）
        await ctx.send(view=view)

async def setup(bot):
    await bot.add_cog(Role(bot))
