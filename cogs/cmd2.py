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

# 發送嵌入訊息
async def send_embed_message(ctx, content, color=discord.Color.blue()):
    embed = discord.Embed(
        description=content,
        color=color  # 設定訊息的顏色
    )
    await ctx.send(embed=embed)

# 定義名為 Main 的 Cog
class cmd2(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # $nuke 指令：一次清空指定頻道中的所有訊息
    @commands.command()
    @commands.has_permissions(manage_messages=True) 
    async def nuke(self, ctx, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel
        

        if not channel.permissions_for(ctx.guild.me).manage_messages:
            await send_embed_message(ctx, "我無權刪除此頻道中的消息", color=discord.Color.red())
            return

        try:
            await channel.purge(limit=None)
            await send_embed_message(ctx, f"成功刪除了所有訊息{channel.mention}.", color=discord.Color.green())
        except discord.Forbidden:
            await send_embed_message(ctx, "我無權刪除此頻道中的消息", color=discord.Color.red())
        except discord.HTTPException:
            await send_embed_message(ctx, "清除通道時發生錯誤", color=discord.Color.red())

    # $autonuke 指令：一次清空所有頻道中的所有訊息
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def autonuke(self, ctx):
        if not ctx.guild.me.guild_permissions.manage_messages:
            await send_embed_message(ctx, "我沒有權限刪除所有頻道中的消息", color=discord.Color.red())
            return
        
        try:
            for channel in ctx.guild.text_channels:

                if channel.permissions_for(ctx.guild.me).manage_messages:
                    await channel.purge(limit=None)
                    await send_embed_message(ctx, f"成功刪除全部頻道的訊息 {channel.mention}.", color=discord.Color.green())
                else:
                    await send_embed_message(ctx, f"我無權刪除頻道訊息 {channel.mention}.", color=discord.Color.red())
        except discord.Forbidden:
            await send_embed_message(ctx, "我無權刪除某些頻道中的消息", color=discord.Color.red())
        except discord.HTTPException:
            await send_embed_message(ctx, "清除通道時發生錯誤", color=discord.Color.red())
        # $purge 指令：刪除指定數量的訊息
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        # 檢查是否有刪除訊息的權限
        if not ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await send_embed_message(ctx, "我無權刪除此頻道中的消息", color=discord.Color.red())
            return

        # 刪除指定數量的訊息
        try:
            deleted = await ctx.channel.purge(limit=amount)
            await send_embed_message(ctx, f"成功刪除{len(deleted)} 訊息在 {ctx.channel.mention}頻道.", color=discord.Color.green())
        except discord.Forbidden:
            await send_embed_message(ctx, "我無權刪除此頻道中的消息.", color=discord.Color.red())
        except discord.HTTPException:
            await send_embed_message(ctx, "刪除訊息時出錯", color=discord.Color.red())
        # $lock 指令：鎖定指定頻道，禁止 everyone 發送訊息
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel

        if not channel.permissions_for(ctx.guild.me).manage_channels:
            await send_embed_message(ctx, "我無法管理此頻道", color=discord.Color.red())
            return

        try:
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await send_embed_message(ctx, f"{channel.mention} 以上鎖. `@everyone` 無法發送訊息.", color=discord.Color.orange())
        except discord.Forbidden:
            await send_embed_message(ctx, "我沒權限管理此頻道", color=discord.Color.red())
        except discord.HTTPException:
            await send_embed_message(ctx, "在上所時發生未知錯誤", color=discord.Color.red())
        # $lock_all 指令：鎖定伺服器中的所有文字頻道
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock_all(self, ctx):
        if not ctx.guild.me.guild_permissions.manage_channels:
            await send_embed_message(ctx, "我沒有管理所有頻道的權限", color=discord.Color.red())
            return

        for channel in ctx.guild.text_channels:
            try:
                overwrite = channel.overwrites_for(ctx.guild.default_role)
                overwrite.send_messages = False
                await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
                await send_embed_message(ctx, f"{channel.mention} 已上鎖. `@everyone` 無法發送訊息。", color=discord.Color.orange())
            except discord.Forbidden:
                await send_embed_message(ctx, f"我無法管理 {channel.mention}", color=discord.Color.red())
            except discord.HTTPException:
                await send_embed_message(ctx, f"在鎖定 {channel.mention} 時發生未知錯誤", color=discord.Color.red())

    # $unlock 指令：解鎖指定頻道，允許 everyone 發送訊息
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel

        if not channel.permissions_for(ctx.guild.me).manage_channels:
            await send_embed_message(ctx, "我無法管理此頻道", color=discord.Color.red())
            return

        try:
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = None  # 重置為預設權限
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await send_embed_message(ctx, f"{channel.mention} 已解鎖. `@everyone` 現可發送訊息。", color=discord.Color.green())
        except discord.Forbidden:
            await send_embed_message(ctx, "我無法管理此頻道", color=discord.Color.red())
        except discord.HTTPException:
            await send_embed_message(ctx, "在解鎖時發生未知錯誤", color=discord.Color.red())

    # $unlock_all 指令：解鎖伺服器中的所有文字頻道
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock_all(self, ctx):
        if not ctx.guild.me.guild_permissions.manage_channels:
            await send_embed_message(ctx, "我沒有管理所有頻道的權限", color=discord.Color.red())
            return

        for channel in ctx.guild.text_channels:
            try:
                overwrite = channel.overwrites_for(ctx.guild.default_role)
                overwrite.send_messages = None
                await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
                await send_embed_message(ctx, f"{channel.mention} 已解鎖. `@everyone` 現可發送訊息。", color=discord.Color.green())
            except discord.Forbidden:
                await send_embed_message(ctx, f"我無法管理 {channel.mention}", color=discord.Color.red())
            except discord.HTTPException:
                await send_embed_message(ctx, f"在解鎖 {channel.mention} 時發生未知錯誤", color=discord.Color.red())




# 在啟動時將 bot 註冊進該 cog
async def setup(bot):
    await bot.add_cog(cmd2(bot))
