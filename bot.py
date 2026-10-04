import os

import discord
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

@client.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name='紀錄')
    if channel is None:
        return

    embed = discord.Embed(
        title='📤 成員離開',
        description=f'{member.mention} 離開了伺服器',
        color=discord.Color.red(),
        timestamp=discord.utils.utcnow(),
    )
    embed.set_author(name=str(member), icon_url=member.display_avatar.url)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name='使用者 ID', value=f'`{member.id}`', inline=True)
    embed.add_field(name='帳號建立', value=discord.utils.format_dt(member.created_at, 'R'), inline=True)
    if member.joined_at:
        embed.add_field(name='加入時間', value=discord.utils.format_dt(member.joined_at, 'F'), inline=False)

    roles = [role.mention for role in reversed(member.roles) if role != member.guild.default_role]
    embed.add_field(name=f'身分組（{len(roles)}）', value=' '.join(roles) if roles else '無', inline=False)
    embed.set_footer(text=f'目前成員數：{member.guild.member_count}')

    await channel.send(embed=embed)

client.run(os.environ['DISCORD_TOKEN'])

