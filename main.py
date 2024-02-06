import apiToken,discord
from discord.ext import commands
import wavelink

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

class CustomPlayer(wavelink.Player):

    def __init__(self):
        super().__init__()
        self.queue = wavelink.Queue()

@client.event
async def on_ready():
    client.loop.create_task(connect_nodes())

@client.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    if message_id == 1128041268379914300:
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g : g.id == guild_id,client.guilds)
        role = discord.utils.get(guild.roles,name = payload.emoji.name)
        if role is not None:
            print(role.name)
            member = discord.utils.find(lambda m :m.id == payload.user_id,guild.members)
            if member is not None:
                await member.add_roles(role)
                print("done")
            else:
                print("Role not found")
@client.event
async def on_raw_reaction_remove(payload):
    message_id = payload.message_id
    if message_id == 1128041268379914300:
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g : g.id == guild_id,client.guilds)
        role = discord.utils.get(guild.roles,name = payload.emoji.name)
        if role is not None:
            print(role.name)
            member = discord.utils.find(lambda m :m.id == payload.user_id,guild.members)
            if member is not None:
                await member.remove_roles(role)
                print("done")
            else:
                print("Role not found")

@client.event
async def on_wavelink_track_end(payload):
    cls = CustomPlayer()
    if not cls.queue.is_empty:
        next_track = cls.queue.get()
        await cls.play(next_track)

async def connect_nodes():
    await client.wait_until_ready()
    node: wavelink.Node = wavelink.Node(uri='http://localhost:2333', password='youshallnotpass')
    await wavelink.NodePool.connect(client=client, nodes=[node])

@client.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f"Node <> is ready!")

@client.command()
async def connect(ctx):
    vc = ctx.voice_client # represents a discord voice connection
    try:
        channel = ctx.author.voice.channel
    except AttributeError:
        return await ctx.send("Please join a voice channel to connect.")

    if not vc:
        await ctx.author.voice.channel.connect(cls=CustomPlayer())
    else:
        await ctx.send("The bot is already connected to a voice channel")

@client.command()
async def disconnect(ctx):
    vc = ctx.voice_client
    if vc:
        await vc.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@client.command()
async def play(ctx, *, search: wavelink.YouTubeTrack):
    vc = ctx.voice_client
    if not vc:
        custom_player = CustomPlayer()
        vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)

    if vc.is_playing():
        embed = discord.Embed(
            title=search.title,
            url=search.uri,
            description="Queued"
        )
        await ctx.send("Your song is queued")
        await ctx.send(embed=embed)

    else:
        await ctx.send(f"{search.title} is playing")
        embed = discord.Embed(
            title=search.title,
            url=search.uri,
            description="Now Playing"
        )
        embed.set_thumbnail(url = search.thumb)
        await ctx.send(embed = embed)
        await vc.play(search)



@client.command()
async def skip(ctx):
    vc = ctx.voice_client
    if vc:
        if not vc.is_playing():
            return await ctx.send("Nothing is playing.")
        if vc.queue.is_empty:
            return await vc.stop()

        await vc.seek(vc.track.length * 1000)
        if vc.is_paused():
            await vc.resume()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@client.command()
async def pause(ctx):
    vc = ctx.voice_client
    if vc:
        if vc.is_playing() and not vc.is_paused():
            await vc.pause()
        else:
            await ctx.send("Nothing is playing.")
    else:
        await ctx.send("The bot is not connected to a voice channel")


@client.command()
async def resume(ctx):
    vc = ctx.voice_client
    if vc:
        if vc.is_paused():
            await vc.resume()
        else:
            await ctx.send("Nothing is paused.")
    else:
        await ctx.send("The bot is not connected to a voice channel")


@play.error
async def play_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Could not find a track.")
    else:
        await ctx.send("Please join a voice channel.")


client.run(apiToken.TOKEN)