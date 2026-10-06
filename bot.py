import datetime
import io
import os

import discord
from discord.ext import tasks
from dotenv import load_dotenv

import sheet_snapshot

load_dotenv()

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

# 台灣沒有日光節約時間，用固定 UTC+8 即可
TAIPEI = datetime.timezone(datetime.timedelta(hours=8))
# 每週排程截圖：星期幾（週一為 0）→（試算表範圍, 訊息標題）
WEEKLY_SNAPSHOTS = {
    3: ('A31:P62', '週四城戰隊伍攻城表'),
    6: ('R31:AG62', '週日決戰隊伍表'),
}

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    if not weekly_sheet_snapshot.is_running():
        weekly_sheet_snapshot.start()

@tasks.loop(time=datetime.time(hour=20, minute=0, tzinfo=TAIPEI))
async def weekly_sheet_snapshot():
    now = datetime.datetime.now(TAIPEI)
    snapshot = WEEKLY_SNAPSHOTS.get(now.weekday())
    if snapshot is None:
        return

    cell_range, title = snapshot
    png = await sheet_snapshot.capture(cell_range)
    filename = f'sheet-{now:%Y%m%d}.png'
    for guild in client.guilds:
        channel = discord.utils.get(guild.text_channels, name='紀錄')
        if channel is None:
            continue
        await channel.send(
            f'📊 {now:%Y/%m/%d} {title}',
            file=discord.File(io.BytesIO(png), filename=filename),
        )

@weekly_sheet_snapshot.error
async def on_weekly_sheet_snapshot_error(error):
    print(f'[weekly_sheet_snapshot] 截圖失敗：{error!r}')

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

