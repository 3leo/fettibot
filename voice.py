import discord
import os
import youtube_dl
from discord.ext import commands

def setup(client):
    @client.command(name='play')
    async def play(ctx, url: str):
        song_there = os.path.isfile("song.mp3")
        try:
            if song_there:
                os.remove("song.mp3")
        except PermissionError:
            await ctx.send("Wait for the current playing music to end or use the 'stop' command")
            return

        voice_channel = discord.utils.get(ctx.guild.voice_channels, name='General')
        await voice_channel.connect()
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            for file in os.listdir("./"):
                if file.endswith(".mp3"):
                    os.rename(file, "song.mp3")
                    voice.play(discord.FFmpegPCMAudio("song.mp3"))

    @client.command(name='leave')
    async def leave(ctx):
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.disconnect()
        else:
            await ctx.send("The bot is not connected to a voice channel.")

    @client.command(name='pause')
    async def pause(ctx):
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice and voice.is_playing():
            voice.pause()
        else:
            await ctx.send("Currently no audio is playing.")

    @client.command(name='resume')
    async def resume(ctx):
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice and voice.is_paused():
            voice.resume()
        else:
            await ctx.send("The audio is not paused.")
