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
        await ctx.channel.send(f'사용법을 참고해주세요. ({PREFIX}도움)')
        return

    await ctx.channel.trigger_typing()                # 봇 상태를 타이핑중으로 변경.

    date = ''
    if len(args) > 1:
        delta_day = DeltaDay.str_to(args[1])                 # 델타 날짜(어제/오늘/내일/모레 등) 인가?

        if delta_day is not DeltaDay.UNKNOWN:
            date = datetime(datetime.today().year, datetime.today().month, datetime.today().day, 0, 0, 0, 0) + timedelta(days=delta_day.value)
        else:
            # 델타 날짜가 아니라면 일반 날짜(YYYY-mm-dd)로 인식
            try:
                date = datetime.strptime(args[1], '%Y-%m-%d')
            except:
                await ctx.channel.send('날짜 형식이 잘못 되었습니다.')
                return
    else:
        date = datetime(datetime.today().year, datetime.today().month, datetime.today().day, 0, 0, 0, 0)        # 추가 인자 없으면 오늘로 설정

    cafeteria_name = args[0]
    cafe_info = categorize_cafe_name(cafeteria_name)
    cafe_type = cafe_info[0]
    cafe_detail_type = cafe_info[1]

    week_menu_list = ''
    try:
        week_menu_list = parse_zzam(cafe_type, cafe_detail_type, date)           # 식당, 날짜를 특정하여 해당되는 주의 모든 메뉴 파싱
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


# 파싱한 메뉴 배열 중 요청한 날짜의 메뉴만 반환
def fetch_menu_by_date(menu_list, date):
    target_menu_list = []
    for m in menu_list:
        if m._date.strftime('%Y-%m-%d') == date.strftime('%Y-%m-%d'):
            target_menu_list.append(m)

    return target_menu_list
    

def menu_to_embed(menu):
    day_of_week_text = DayOfWeek.to_str(DayOfWeek.int_to_dow(menu._date.weekday()))
    date_simple_text = menu._date.strftime('%m.%d') + ' (' + day_of_week_text + ')'
    cafe_type_text = '알수없음'
    meal_time_text = MealTimeType.to_str(menu._meal_time_type)
    date_full_text = menu._date.strftime('%Y-%m-%d')
    emoji = MealTimeType.to_emoji(menu._meal_time_type)

    # 교내식당/기숙사 구분 후 식당이름 지정
    if menu._cafe_type is CafeteriaType.NORM:
        cafe_type_text = NormCafeType.to_str(menu._cafe_detail_type)
    elif menu._cafe_type is CafeteriaType.DORM:
        cafe_type_text = DormCafeType.to_str(menu._cafe_detail_type)

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

    


# 사용자로부터 입력받은 식당이름을 가지고 좀 더 명확히 만든다. 
# 첫 인덱스에는 교내식당/기숙사 구별, 두번째 인덱스에는 어느 식당인지 저장하여 반환함.
def categorize_cafe_name(cafeteria_name):
    resultArr = []

    cafe_type = CafeteriaType.UNKNOWN
    cafe_detail_type = NormCafeType.UNKNOWN

    if cafeteria_name in ['학생식당', '학생', '학식당', '학식', '학']:
        cafe_type = CafeteriaType.NORM
        cafe_detail_type = NormCafeType.STUDENT
    elif cafeteria_name in ['교직원식당', '교직원', '교식당', '교식', '교']:
        cafe_type = CafeteriaType.NORM
        cafe_detail_type = NormCafeType.STAFF
    elif cafeteria_name in ['분식당', '분식', '분']:
        cafe_type = CafeteriaType.NORM
        cafe_detail_type = NormCafeType.SNACKBAR
    elif cafeteria_name in ['푸름관', '푸름', '푸']:
        cafe_type = CafeteriaType.DORM
        cafe_detail_type = DormCafeType.PUROOM
    elif cafeteria_name in ['오름관1동', '오름1', '오1', '1동']:
        cafe_type = CafeteriaType.DORM
        cafe_detail_type = DormCafeType.OREUM1
    elif cafeteria_name in ['오름관3동', '오름3', '오3', '3동']:
        cafe_type = CafeteriaType.DORM
        cafe_detail_type = DormCafeType.OREUM3

    resultArr.append(cafe_type)
    resultArr.append(cafe_detail_type)

    return resultArr


# 식당, 날짜를 특정하여 해당되는 주의 모든 메뉴 파싱
def parse_zzam(cafeteria_type, detail_type, date):
    if cafeteria_type is CafeteriaType.NORM:
        return parse_cafeteria(detail_type, date)
    elif cafeteria_type is CafeteriaType.DORM:
        return parse_dorm(detail_type, date)
    else:
        raise Exception('unknown CafeteriaType')


def parse_cafeteria(detail_type, date):
    print('parse cafeteria')

    session = requests.Session()

    URL = ''

    # 학생식당/교직원식당/분식당별 URL 설정
    if detail_type is NormCafeType.STUDENT:
        URL = STUDENT_CAFETERIA_URL
    elif detail_type is NormCafeType.STAFF:
        URL = STAFF_CAFETERIA_URL
    elif detail_type is NormCafeType.SNACKBAR:
        URL = SNACKBAR_URL
    else:
        raise Exception('unknown NormCafeType')

    # URL용 날짜 설정 (찾기 원하는 날짜가 일요일이면 달력이 넘어가서 하루 빼주고 파싱함)
    url_date = date
    if url_date.weekday() is 6:
        url_date -= timedelta(days=1)
    URL += 'mode=menuList&srDt=' + url_date.strftime('%Y-%m-%d')

    # 파싱 리퀘스트
    menu_req = session.get(URL)

    menu_req_html = BeautifulSoup(menu_req.text, 'html.parser')

    # 등록된 메뉴가 있는지 체크
    menu_exist_check_html = menu_req_html.select('table > tbody > td')
    if menu_exist_check_html:
        raise Exception('등록된 메뉴가 없습니다.')

    # 시작 날짜 겟
    menu_start_date_html = menu_req_html.select('fieldset > div > div > p')
    start_date_text = menu_start_date_html[0].text.replace('\t','').replace('\n','').replace('\r','')
    start_date_text = start_date_text.split('~')[0]
    start_date = datetime.strptime(start_date_text, '%Y.%m.%d')

    # 메뉴 겟
    menu_list_html = menu_req_html.select('table > tbody > tr > td')
    cnt = 0
    resultArr = []

    for menu_html in menu_list_html:
        meal_time_txt = menu_html.select('p')[0].text
        meal_time_type = MealTimeType.UNKNOWN

        if detail_type is NormCafeType.SNACKBAR:
            meal_time_type = MealTimeType.ONECOURSE
        else:
            if meal_time_txt == MealTimeType.to_str(MealTimeType.LUNCH):
                meal_time_type = MealTimeType.LUNCH
            elif meal_time_txt == MealTimeType.to_str(MealTimeType.DINNER):
                meal_time_type = MealTimeType.DINNER
            elif meal_time_txt == MealTimeType.to_str(MealTimeType.BREAKFAST):
                meal_time_type = MealTimeType.BREAKFAST

        menu_detail_html = menu_html.select('ul > li')
        menu_elems = []

        for menu_elem_html in menu_detail_html:
            elem_txt = menu_elem_html.text
            menu_elems.append(elem_txt)

        # 메뉴 객체 생성
        menu_date = start_date + timedelta(days=cnt%7)
        m = Menu(CafeteriaType.NORM, detail_type, menu_date, meal_time_type, menu_elems)
        resultArr.append(m)
        cnt += 1

    print('successfully parsed')
    return resultArr


def parse_dorm(detail_type, date):
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