import discord
import asyncio
import traceback
import sys
from config import config
from datetime import datetime, timezone, timedelta


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
WORKING_CHANNEL = config().channel_id
TOKEN = config.token

channel = None

tz = timezone(timedelta(hours=9))
NOTIFI_TIME = (19, 0)

event_name: dict[tuple[int, int], str] = {}
event_delete: dict[tuple[int, int], asyncio.events.TimerHandle] = {}


def alarm():
    channel = client.get_channel(WORKING_CHANNEL)
    try:
        a = asyncio.get_running_loop()
        t = datetime.now(tz)
        try:
            name = event_name[(t.month, t.day)] + " "
        except KeyError:
            asyncio.run_coroutine_threadsafe(channel.send("名前がわからないMTGがあります。"), a)
        asyncio.run_coroutine_threadsafe(channel.send(name + "のMTG開いてください"), a)
        del event_name[(t.month, t.day)]
        del event_delete[(t.month, t.day)]
    except Exception as e:
        asyncio.run(channel.send("".join(traceback.format_exception(*sys.exc_info()))))


async def set_alarm(month, day, name):
    try:
        t = datetime.now(tz)
        target = t.replace(
            month=month,
            day=day,
            hour=NOTIFI_TIME[0],
            minute=NOTIFI_TIME[1],
            second=0,
            microsecond=0,
        )
        if target < t:
            target = target.replace(year=target.year + 1)
            channel = client.get_channel(WORKING_CHANNEL)
            await channel.send("来年の")
        a = asyncio.get_running_loop()
        if (month, day) in event_delete:
            event_name[(month, day)] += "&" + name
        else:
            event_name[(month, day)] = name
            event_delete[(month, day)] = a.call_later(
                (target - t).total_seconds(), alarm
            )
    except Exception as e:
        channel = client.get_channel(WORKING_CHANNEL)
        await channel.send("".join(traceback.format_exception(*sys.exc_info())))


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    channel = client.get_channel(WORKING_CHANNEL)
    await channel.send("I'm ready.")


@client.event
async def on_message(message: discord.Message):
    try:
        global tz
        if message.author == client.user:
            return
        if message.channel.id != WORKING_CHANNEL:
            return

        order = message.content.split()
        if order[0] == "mbot":
            if len(order) == 1:
                await message.channel.send("I'm ready.")
                return
            try:
                if order[1] == "notify":
                    c = order[2].split("/")
                    if len(order) == 4:
                        name = order[3]
                    else:
                        name = "ミーティング"
                    await set_alarm(int(c[0]), int(c[1]), name)
                    await message.channel.send(f"{c[0]}月{c[1]}日にお伝えします")
                elif order[1] == "mtg":
                    c = order[2].split("/")
                    target = datetime.now(tz).replace(month=int(c[0]), day=int(c[1]))
                    name = order[3] + " "
                    l = [70, 40, 10]
                    if len(order[4:]) != 0:
                        l = list(map(int, order[4:]))
                    for i in l:
                        t = target - timedelta(days=i)
                        await set_alarm(t.month, t.day, name)
                        await message.channel.send(f"{t.month}月{t.day}日")
                    await message.channel.send("にお知らせします。")
                elif order[1] == "del":
                    c = order[2].split("/")
                    n = (int(c[0]), int(c[1]))
                    try:
                        event_delete[(n[0], n[1])].cancel()
                    except KeyError:
                        await message.channel.send("存在しない日付です")
                    else:
                        await message.channel.send(f"{event_name[(n[0], n[1])]}を削除しました")
                        del event_delete[(n[0], n[1])]
                        del event_name[(n[0], n[1])]
                elif order[1] == "show":
                    await message.channel.send(
                        f"{NOTIFI_TIME[0]}時{NOTIFI_TIME[1]}分にお知らせします"
                    )
                    for (a, b), j in event_name.items():
                        await message.channel.send(f"{a}/{b} {j}")
                elif order[1] == "time":
                    await message.channel.send(str(datetime.now(tz)))
                else:
                    await message.channel.send("認識されないコマンドが入力されました")
            except IndexError as e:
                await message.channel.send("必要な引数が入力されてません")
                raise e
            except ValueError as e:
                await message.channel.send("不正な引数が入力されました")
                raise e
    except Exception as e:
        await message.channel.send("".join(traceback.format_exception(*sys.exc_info())))


if __name__ == "__main__":
    client.run(TOKEN)
