import requests
import os
import urllib
import io
import shutil

from datetime import datetime
from io import BytesIO
from bs4 import BeautifulSoup
from discord import Game, Embed, File
from discord.ext import commands
from dotenv import load_dotenv
from requests import get
from urllib import parse

load_dotenv()  # load bot environment

BOT_TOKEN = ""
PREFIX = ""

STUDENT_CAFETERIA_URL = ""
STAFF_CAFETERIA_URL = ""
SNACKBAR_URL = ""
DORM_PUROOM_URL = ""
DORM_OREUM1_URL = ""
DORM_OREUM3_URL = ""

def load_env():
    global BOT_TOKEN
    global PREFIX

    BOT_TOKEN = get_env_var('BOT_TOKEN')
    PREFIX = get_env_var('PREFIX')

    STUDENT_CAFETERIA_URL = get_env_var('STUDENT_CAFETERIA_URL')
    STAFF_CAFETERIA_URL = get_env_var('STAFF_CAFETERIA_URL')
    SNACKBAR_URL = get_env_var('SNACKBAR_URL')
    DORM_PUROOM_URL = get_env_var('DORM_PUROOM_URL')
    DORM_OREUM1_URL = get_env_var('DORM_OREUM1_URL')
    DORM_OREUM3_URL = get_env_var('DORM_OREUM3_URL')

def get_env_var(var_name):
    result = os.getenv(var_name)
    if not result:
        raise Exception(f'no {var_name}')
    return result

def from_text(ctx):
    # msg_fr = msg.server.name + ' > ' + msg.channel.name + ' > ' + msg.author.name
    # msg.server --> msg.guild
    # https://discordpy.readthedocs.io/en/latest/migrating.html#server-is-now-guild
    
    channel_type = ctx.channel.type.value
    if channel_type == 1:
        return f'DM > {ctx.author.name}'

    else:
        return f'{ctx.guild.name} > {ctx.channel.name} > {ctx.author.name}'

def log(fr, text):
    print(f'{fr} | {str(datetime.now())} | {text}')  # TODO: 시간대 조정


bot = commands.Bot("")


@bot.event
async def on_ready():
    log('SYSTEM', 'bot ready')
    log('SYSTEM', 'PREFIX : ' + PREFIX)
    await bot.change_presence(activity=Game(name=f'{PREFIX}도움'))

#@bot.event
#async def on_message(message):
#    if message.content.startswith('$greet'):
#        channel = message.channel
#        await channel.send('Say hello!')


@bot.command(name='도움')
async def help(ctx):
    log(from_text(ctx), 'help command')
    print("도움")


# $짬 -> 이번 식단들 모두 표시 (기숙사+학식당) (점심시간이면 점심, 저녁시간이면 저녁)
# $짬 [식당] -> 오늘 해당식당 메뉴 표기
# $짬 [식당] [날짜] -> 해당 날짜의 해당 식당 메뉴 표기
# (+ embed로 표시하고, 아래쪽에 좌우 화살표로 넘길 수 있게?)
@bot.command(name='짬')
async def zzam(ctx, *args):
    log(from_text(ctx), 'zzam command')

    #if not args or len(args) > 2:
    #    log(from_text(ctx), 'empty args')
    #    await ctx.channel.send(f'사용법을 참고해주세요. ({PREFIX}도움)')
    #    return

    # await ctx.channel.trigger_typing()      # 타이핑중으로 변경.

    # zzam 호출 -> 받은 인자로 타입 구별 -> parse_zzam에 식당/시간 정보 넘겨줌 -> parse_zzam에서 타입에 맞게 긱사/학식당 메뉴 파싱 -> 적절한 형태로 변환해서 반환
    parse_zzam()

def parse_zzam(type):
    if type is 1:
        parse_cafeteria()
    else:
        parse_dorm()

def parse_cafeteria():
    print('parse cafeteria')

    session = requests.Session()

    package_search_req = session.get(STUDENT_CAFETERIA_URL)

    package_search_html = BeautifulSoup(package_search_req.text, 'html.parser')

def parse_dorm():
    print('parse_dorm')


# $평가 [식당] -> 이번 메뉴 목록 (점심이면 점심, 저녁시간이면 저녁) 표시하고 평가받을 수 있게
# $평가 [식당] [아침/점심/저녁] -> 메뉴 목록 보여주고 아래쪽에 reaction으로 점수 평가받을 수 있게? 1~5점 + 취소버튼)
@bot.command(name='평가')
async def score(ctx, *args):
    print('score')

@bot.event
async def on_command_error(ctx, error):
    log(from_text(ctx), error)
    await ctx.channel.send(error)


if __name__ == "__main__":
    try:
        load_env()
        bot.command_prefix = PREFIX
        bot.run(BOT_TOKEN)
    except Exception as e:
        print('load env failed.', e)
