import discord
from discord.ext import commands
import random

# 設定檔案名稱
intents = discord.Intents.default()
intents.guilds = True
intents.members = True  # 需要成員加入和離開的事件
intents.messages = True  # 需要處理消息事件

# 定義隨機的句子列表
phrases = [
    "https://tenor.com/rDEfekv9pxu.gif",
    "https://tenor.com/lBdmtlgQIrM.gif",
    "https://tenor.com/bYLTy.gif",
    "https://tenor.com/crYDiAHRroy.gif",
    "https://tenor.com/qULccx3WPvk.gif",
    "https://tenor.com/kSfuact6pqF.gif",
    "https://tenor.com/biv0Y.gif",
    "https://tenor.com/b1yp8.gif",
    "https://tenor.com/bscAT.gif",
    "https://tenor.com/bJ8Sy.gif",
    "https://tenor.com/hsAszyCpkPh.gif",
    "https://tenor.com/fB2kjlKHIgK.gif",
    "https://tenor.com/9r0t.gif",
    "https://tenor.com/pYTs0JKYqsG.gif",
    "https://tenor.com/bSnwh.gif",
    "https://tenor.com/nolL4QdFgi2.gif",
    "https://tenor.com/bwSRa.gif",
    "https://tenor.com/bBit1.gif",
    "https://tenor.com/bz3gM.gif",
    "https://tenor.com/bHbNa.gif",
    "https://tenor.com/bSaaX.gif",
    "https://tenor.com/bwSPh.gif",
    "https://tenor.com/cdfQrDkbee3.gif",
    "https://tenor.com/mwUlJbVRFsl.gif",
    "https://tenor.com/rgeWz8CkhqT.gif",
    "https://tenor.com/kUYvbL51b7p.gif",
    "https://tenor.com/brFDpYIrPcY.gif",
    "https://tenor.com/o5tFbwUwCsK.gif",
    "https://tenor.com/olThUjgHX68.gif",
    "https://tenor.com/bArgw.gif",
    "https://tenor.com/9CWv.gif",
    "https://tenor.com/bgBDEWVxSF3.gif",
    "https://tenor.com/hRUXCvGKVyv.gif",
    "https://tenor.com/j9RIOo426qW.gif",
    "https://tenor.com/bMgYW.gif",
    "https://tenor.com/bxEwT.gif",
    "https://tenor.com/bSysK.gif",
    "https://tenor.com/czJWPaizs3S.gif",
    "https://tenor.com/bCYHe.gif",
    "https://tenor.com/tq0UXQlp2Kc.gif",
    "https://tenor.com/tmrsCe8BzCF.gif",
    "https://tenor.com/bTjP4.gif",
    "https://tenor.com/bjsEJ.gif",
    "https://tenor.com/sKSbBIlqpnJ.gif",
    "https://tenor.com/bOBCM.gif",
    "https://tenor.com/lLFQuN86l9N.gif",
    "https://tenor.com/bUE13.gif"
]

catmeme = [
    "https://tenor.com/9DYH.gif",
    "https://tenor.com/uZ0jQs3E3H4.gif",
    "https://tenor.com/k6wIpgxsbWJ.gif",
    "https://tenor.com/bQ50H.gif",
    "https://tenor.com/h61LAaXBf2c.gif",
    "https://tenor.com/bN3Rz.gif",
    "https://tenor.com/uYqQ8kreXBw.gif",
    "https://tenor.com/bgk5glPKqlx.gif",
    "https://tenor.com/lfi3l93Xoho.gif",
    "https://tenor.com/dqqjqzrnbLH.gif",
    "https://tenor.com/jnHVKIsc5tB.gif",
    "https://tenor.com/vGe6OIBI6Mo.gif",
    "https://tenor.com/bvAQP.gif",
    "https://tenor.com/bVbzD.gif",
    "https://tenor.com/gAaVOSeV7qu.gif",


]



# 定義 gif 指令的 Cog
class gif(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 定義 gif 指令
    @commands.command()
    async def black(self, ctx):
        # 隨機選擇一句話
        random_phrase = random.choice(phrases)  # 隨機選擇一個句子
        await ctx.send(random_phrase)  # 直接發送純文本消息到 Discord 頻道
    @commands.command()
    async def cat(self, ctx):
        # 隨機選擇一句話
        random_phrase1 = random.choice(catmeme)  # 隨機選擇一個句子
        await ctx.send(random_phrase1)  # 直接發送純文本消息到 Discord 頻道

# 在啟動時將 bot 註冊進該 cog
async def setup(bot):
    await bot.add_cog(gif(bot))
