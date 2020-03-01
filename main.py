import requests
import os
import urllib
import obj
import datetime

from io import BytesIO
from bs4 import BeautifulSoup
from discord import Game, Embed, File
from discord.ext import commands
from dotenv import load_dotenv
from requests import get
from urllib import parse
from obj import *
from datetime import datetime, timedelta

load_dotenv()  # load bot environment

BOT_TOKEN = ""
PREFIX = ""
EMBED_COLOR = 0x00D1FF

STUDENT_CAFETERIA_URL = ""
STAFF_CAFETERIA_URL = ""
SNACKBAR_URL = ""
DORM_PUROOM_URL = ""
DORM_OREUM1_URL = ""
DORM_OREUM3_URL = ""

bot = commands.Bot("")

def load_env():
    global BOT_TOKEN, PREFIX, STUDENT_CAFETERIA_URL, STAFF_CAFETERIA_URL, SNACKBAR_URL, DORM_PUROOM_URL, DORM_OREUM1_URL, DORM_OREUM3_URL

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


# $짬 [식당] -> 오늘 해당식당 메뉴 표기
# $짬 [식당] [날짜] -> 해당 날짜의 해당 식당 메뉴 표기
# $짬 [식당] [오늘/내일/모레/어제/월요일~일요일]
# (+ embed로 표시하고, 아래쪽에 좌우 화살표로 넘길 수 있게?)
# (+ DM으로 보내줄까 아니면 채팅방에 띄울까?)
# (+ n초뒤 자동으로 삭제?)
@bot.command(name='짬')
async def zzam(ctx, *args):
    log(from_text(ctx), 'zzam command')

    if not args or len(args) > 2:
        log(from_text(ctx), 'empty args')
        await ctx.channel.send(f'사용법 : {PREFIX}짬 [식당] [옵션-날짜]\n자세히 : {PREFIX}도움')
        return

    await ctx.channel.trigger_typing()                          # 봇 상태를 타이핑중으로 변경.

    user_input = args[1]

    if len(args) > 1:
        date = normalize_date(user_input)
    else:
        date = datetime(datetime.today().year, datetime.today().month, datetime.today().day, 0, 0, 0, 0)        # 탐색 시간을 오늘로 설정

    cafeteria_name = args[0]
    cafe_type = CafeteriaType.str_to(cafeteria_name)

    week_menu_list = ''
    try:
        week_menu_list = parse_zzam(cafe_type, date)           # 식당, 날짜를 특정하여 해당되는 주의 모든 메뉴 파싱
    except Exception as e:
        await ctx.channel.send(e)
        return

    target_menu_list = fetch_menu_by_date(week_menu_list, date)                  # 요청한 날짜의 메뉴만 남김

    # 메뉴가 존재하면 메시지 전송
    if target_menu_list:
        for m in target_menu_list:
            embed = menu_to_embed(m)
            await ctx.channel.send(embed=embed)

        log(from_text(ctx), 'zzam success')
    else:
        await ctx.channel.send('해당 날짜에 해당되는 식단이 없습니다.')
        log(from_text(ctx), 'zzam no result from week_menu_list')


# 문자열 날짜가 델타 날짜(어제/오늘/모레)인지, 요일(월/화/수)인지, 일반타입(YYYY-mm-nn)인지 구별하여 정규화하여 반환함.
def normalize_date(date_str):
    date = datetime(datetime.today().year, datetime.today().month, datetime.today().day, 0, 0, 0, 0)        # 탐색 시간을 일단 오늘로 설정

    if DeltaDay.is_delta_day(date_str):
        delta_day = DeltaDay.str_to(date_str)
        date += timedelta(days=delta_day.value)               # 델타 날짜이면 현재로부터 delta 날짜만큼 조정한다.

    elif DayOfWeek.is_day_of_week(date_str):
        day_of_week = DayOfWeek.str_to(date_str)
        diff = 0 - (date.weekday() - day_of_week.value)
        date += timedelta(days=diff)                          # 요일이면 현재 요일로부터 대상 요일만큼 조정한다.

    else:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')    # 델타 날짜가 아니라면 일반 날짜(YYYY-mm-dd)로 인식
        except:
            raise Exception('날짜 형식이 잘못 되었습니다.')

    return date


# 파싱한 메뉴 배열 중 요청한 날짜의 메뉴만 반환
def fetch_menu_by_date(menu_list, date):
    target_menu_list = []
    for m in menu_list:
        if m._date.strftime('%Y-%m-%d') == date.strftime('%Y-%m-%d'):
            target_menu_list.append(m)

    return target_menu_list

    
# 전송을 위해 한 식단을 embed
def menu_to_embed(menu):
    day_of_week_text = DayOfWeek.to_str(DayOfWeek.int_to_dow(menu._date.weekday()))
    date_simple_text = menu._date.strftime('%m.%d') + ' (' + day_of_week_text + ')'
    cafe_type_text = '알수없음'
    meal_time_text = MealTimeType.to_str(menu._meal_time_type)
    date_full_text = menu._date.strftime('%Y-%m-%d')
    emoji = MealTimeType.to_emoji(menu._meal_time_type)

    # 식당이름 enum화
    cafe_type_text = CafeteriaType.to_str(menu._cafe_type)

    # 메뉴 배열 텍스트화
    menu_elems_txt = ''
    if menu._menu_elems:
        for e in menu._menu_elems:
            menu_elems_txt += e + '\n'
    else:
        menu_elems_txt = '정보 없음'

    # 임베드 생성
    embed = Embed(title=f'{cafe_type_text} {meal_time_text} {emoji} {date_simple_text}',
                  description=f'{menu_elems_txt}',
                  color=EMBED_COLOR)
    embed.set_footer(text=f'{date_full_text}')
    return embed


# 식당에 알맞는 URL 설정 및 날짜 설정 후 파싱 시도
def parse_zzam(cafeteria_type, date):

    is_dormitory = False
    URL = ''

    # 학생식당/교직원식당/분식당별 URL 설정
    if cafeteria_type is CafeteriaType.STUDENT:
        URL = STUDENT_CAFETERIA_URL
    elif cafeteria_type is CafeteriaType.STAFF:
        URL = STAFF_CAFETERIA_URL
    elif cafeteria_type is CafeteriaType.SNACKBAR:
        URL = SNACKBAR_URL
    elif cafeteria_type is CafeteriaType.PUROOM:
        URL = DORM_PUROOM_URL
        is_dormitory = True
    elif cafeteria_type is CafeteriaType.OREUM1:
        URL = DORM_OREUM1_URL
        is_dormitory = True
    elif cafeteria_type is CafeteriaType.OREUM3:
        URL = DORM_OREUM3_URL
        is_dormitory = True
    else:
        raise Exception('알 수 없는 식당 유형입니다.')

    # URL용 날짜 설정 (찾기 원하는 날짜가 일요일이면 달력이 넘어가서 하루 빼주고 파싱함)
    url_date = date
    if url_date.weekday() is 6:
        url_date -= timedelta(days=1)
    URL += 'mode=menuList&srDt=' + url_date.strftime('%Y-%m-%d')

    # 학교홈페이지에서 파싱할지 기숙사페이지에서 파싱할지 결정
    if is_dormitory:
        return parse_dormpage(URL, cafeteria_type, date)
    else:
        return parse_homepage(URL, cafeteria_type, date)
        


def parse_homepage(url, cafeteria_type, date):
    # 파싱 리퀘스트
    session = requests.Session()
    menu_req = session.get(url)
    menu_req_html = BeautifulSoup(menu_req.text, 'html.parser')

    # 등록된 메뉴가 있는지 체크
    menu_exist_check_html = menu_req_html.select('table > tbody > td')
    if menu_exist_check_html:
        raise Exception('등록된 메뉴가 없습니다.')

    # 이번주의 시작 날짜 겟
    menu_start_date_html = menu_req_html.select('fieldset > div > div > p')
    start_date_text = menu_start_date_html[0].text.replace('\t','').replace('\n','').replace('\r','')
    start_date_text = start_date_text.split('~')[0]
    start_date = datetime.strptime(start_date_text, '%Y.%m.%d')

    # 이번주 모든 메뉴 겟
    menu_list_html = menu_req_html.select('table > tbody > tr > td')
    cnt = 0
    resultArr = []

    # 이번주 요일별 탐색
    for menu_html in menu_list_html:
        # 조식/중식/석식인지 알아내기
        parsed_meal_time = menu_html.select('p')[0].text
        meal_time_type = MealTimeType.UNKNOWN

        if cafeteria_type is CafeteriaType.SNACKBAR:                # 분식당인 경우 일품요리로 고정
            meal_time_type = MealTimeType.ONECOURSE
        else:
            meal_time_type = MealTimeType.str_to(parsed_meal_time)

        menu_detail_html = menu_html.select('ul > li')
        menu_elems = []

        # 한 요일 내 메뉴들 탐색
        for menu_elem_html in menu_detail_html:
            menu_elems.append(menu_elem_html.text)

        # 메뉴 객체 생성
        menu_date = start_date + timedelta(days=cnt%7)
        m = Menu(cafeteria_type, menu_date, meal_time_type, menu_elems)
        resultArr.append(m)
        cnt += 1

    print('hompage successfully parsed')
    return resultArr


def parse_dormpage(url, cafeteria_type, date):
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