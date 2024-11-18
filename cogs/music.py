import discord
from discord.ext import commands
import asyncio
import yt_dlp as youtube_dl
import json
import os
from dotenv import load_dotenv

intents = discord.Intents().all()
client = discord.Client(intents=intents)
load_dotenv()

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        if 'title' not in data:
            raise ValueError("Couldn't extract title.")
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename, data

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 加入語音頻道
    @commands.command()
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel")
            return
        else:
            channel = ctx.message.author.voice.channel
        await channel.connect()

    # 離開語音頻道
    @commands.command()
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
        else:
            await ctx.send("The bot is not connected to a voice channel.")

    # 播放音樂
    @commands.command()
    async def play(self, ctx, url):
        try:
            server = ctx.message.guild
            voice_channel = server.voice_client

            async with ctx.typing():
                # Download the audio from the URL
                filename, data = await YTDLSource.from_url(url, loop=ctx.bot.loop)

                # Define a function to play the audio in a loop
                def after_playing(error):
                    if error:
                        print(f'Error occurred: {error}')
                    else:
                        voice_channel.play(discord.FFmpegPCMAudio(executable="C:\\ffmpeg\\bin\\ffmpeg.exe", source=filename), after=after_playing)

                # Start playing the audio
                voice_channel.play(discord.FFmpegPCMAudio(executable="C:\\ffmpeg\\bin\\ffmpeg.exe", source=filename), after=after_playing)

            await ctx.send(f'**現在播放：** {data["title"]}')
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    # 停止音樂播放
    @commands.command()
    async def stop(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

# 在啟動時將 bot 註冊進該 cog
async def setup(bot):
    await bot.add_cog(Music(bot))
