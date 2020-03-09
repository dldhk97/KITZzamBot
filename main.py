import requests
import os
import urllib
import obj
import datetime
import asyncio

from io import BytesIO
from bs4 import BeautifulSoup
from discord import Game, Embed, File
from discord.ext import commands
from dotenv import load_dotenv
from requests import get
from urllib import parse
from obj import *
from datetime import datetime, timedelta
from dateutil.parser import parse
from pytz import timezone, utc

load_dotenv()  # load bot environment

BOT_TOKEN = ""
PREFIX = ""
EMBED_COLOR = 0x00D1FF

CAFETERIA_LIST = [CafeteriaType.STUDENT, CafeteriaType.STAFF, CafeteriaType.SNACKBAR, CafeteriaType.PUROOM, CafeteriaType.OREUM1, CafeteriaType.OREUM3]
CAFETERIA_URL = []

INVITE_URL="https://discordapp.com/oauth2/authorize?client_id=683609253575131157&scope=bot&permissions=101440"

KST = timezone('Asia/Seoul')

bot = commands.Bot("")

def load_env():
    global BOT_TOKEN, PREFIX
    BOT_TOKEN = get_env_var('BOT_TOKEN')
    PREFIX = get_env_var('PREFIX')

    CAFETERIA_URL.append(get_env_var('STUDENT_CAFETERIA_URL'))
    CAFETERIA_URL.append(get_env_var('STAFF_CAFETERIA_URL'))
    CAFETERIA_URL.append(get_env_var('SNACKBAR_URL'))
    CAFETERIA_URL.append(get_env_var('DORM_PUROOM_URL'))
    CAFETERIA_URL.append(get_env_var('DORM_OREUM1_URL'))
    CAFETERIA_URL.append(get_env_var('DORM_OREUM3_URL'))


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
    print(f'{fr} | {str(datetime.now(KST))} | {text}')


@bot.event
async def on_ready():
    log('SYSTEM', 'bot ready')
    log('SYSTEM', 'PREFIX : ' + PREFIX)
    await bot.change_presence(activity=Game(name=f'{PREFIX}도움'))


@bot.command(name='도움')
async def help(ctx):
    log(from_text(ctx), 'help command')
    embed = Embed(title='KIT 짬봇 for Discord입니다.',
                  description='명령어들은 아래와 같습니다.',
                  color=EMBED_COLOR)
    embed.add_field(name='사용 방법', value=f'{PREFIX}짬 [옵션-식당명] [옵션-날짜]', inline=False)
    embed.add_field(name='간단 사용', value=f'{PREFIX}짬 학생식당, {PREFIX}짬 푸름관, {PREFIX}짬 오늘, {PREFIX}짬 내일 ...', inline=False)
    embed.add_field(name='축약어 사용', value=f'{PREFIX}짬 학식, {PREFIX}짬 분식, {PREFIX}짬 푸밥, {PREFIX}짬 오3 ...', inline=False)
    embed.add_field(name='날짜 사용', value=f'{PREFIX}짬 푸름관 내일, {PREFIX}짬 푸름관 수요일, {PREFIX}짬 학생식당 2020-01-01 ...', inline=False)
    embed.add_field(name='명령어', value=f'{PREFIX}짬, {PREFIX}도움, {PREFIX}대하여, {PREFIX}초대링크', inline=False)
    embed.add_field(name='식당', value='학생식당, 교직원식당, 분식당, 푸름관, 오름관1동, 오름관3동', inline=False)
    embed.set_footer(text='축약어는 어지간하면 다 됩니다. 학식, 분식, 오3, 푸짬...\n날짜를 안넣으면 오늘 식단을 보여줍니다.')
    await ctx.channel.send(embed=embed)


@bot.command(name='초대링크')
async def help(ctx):
    log(from_text(ctx), 'invite_link command')
    await ctx.channel.send(f'봇 초대 링크 : {INVITE_URL}')


@bot.command(name='대하여')
async def about(ctx):
    log(from_text(ctx), 'about command')
    embed = Embed(title='KIT 짬봇',
                  description='금오공과대학교 식단표를 볼 수 있게 해주는 디스코드 봇입니다.',
                  color=EMBED_COLOR)
    embed.add_field(name='Repository', value='https://github.com/dldhk97/KITZzamBot', inline=False)
    embed.set_footer(text='impressed by dccon hassan. repo : https://github.com/Dogdriip/dccon_hassan')
    await ctx.channel.send(embed=embed)


# $짬 [식당] -> 오늘 해당식당 메뉴 표기
# $짬 [식당] [날짜] -> 해당 날짜의 해당 식당 메뉴 표기
# $짬 [식당] [오늘/내일/모레/어제/월요일~일요일]
# (+ embed로 표시하고, 아래쪽에 좌우 화살표로 넘길 수 있게?)
# (+ DM으로 보내줄까 아니면 채팅방에 띄울까?)
# (+ n초뒤 자동으로 삭제?)
@bot.command(name='짬')
async def zzam(ctx, *args):
    log(from_text(ctx), 'zzam command')

    #if not args or len(args) > 1:
    #    log(from_text(ctx), 'empty args')
    #    await ctx.channel.send(f'사용법 1 : {PREFIX}짬 [식당] [옵션-날짜]\n사용법 2 : {PREFIX}짬 [날짜]\n자세히 : {PREFIX}도움')
    #    return

    await ctx.channel.trigger_typing()                          # 봇 상태를 타이핑중으로 변경.

    if len(args) < 1:
        date = datetime(datetime.today().year, datetime.today().month, datetime.today().day, 0, 0, 0, 0, KST)        # 탐색 시간을 오늘로 설정
        cafe_type = await question_cafeteria(ctx)
        await ctx.channel.trigger_typing()

    else:
        cafe_type = CafeteriaType.str_to(args[0])

        if cafe_type is not CafeteriaType.UNKNOWN:                  # 인자가 식당명일 때
            date = datetime(datetime.today().year, datetime.today().month, datetime.today().day, 0, 0, 0, 0, KST)        # 탐색 시간을 오늘로 설정
        else:
            date = args[0] if len(args) == 1 else args[1]

            try:
                date = normalize_date(date)
                log(from_text(ctx), f'target is {str(date)}')
            except Exception as e:
                await ctx.channel.send('날짜 혹은 식당명이 올바르지 않습니다.')
                log(from_text(ctx), 'wrong date str')
                return

            if len(args) == 1:
                cafe_type = await question_cafeteria(ctx)
                await ctx.channel.trigger_typing()

    week_menu_list = ''

    try:
        week_menu_list = parse_zzam(cafe_type, date)           # 식당, 날짜를 특정하여 해당되는 주의 모든 메뉴 파싱
        log(from_text(ctx), 'week menu parsed')
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

async def question_cafeteria(ctx):
    log(from_text(ctx), 'Question Cafeteria')

    # 식당 목록 생성
    index_emoji_list = []
    cafeteria_list_str = ''
    cnt = 0
    for cafe in CAFETERIA_LIST:
        index_emoji_list.append(EmojiNum(cnt+1).to_emoji_unicode())
        cafeteria_list_str += index_emoji_list[cnt]  + ' ' + cafe.to_str() + '\n'
        cnt += 1

    # embed 메시지 전송
    embed = Embed(title='어떤 식당을 조회할까요?',
                  color=EMBED_COLOR)
    embed.add_field(name='식당 목록', value=cafeteria_list_str, inline=False)
    embed.set_footer(text='알아보고자 하는 식당 번호를 클릭해주세요.')
    message = await ctx.channel.send(embed=embed, delete_after=30)

    # 리액션 달기
    cnt = 0
    for cafe in CAFETERIA_LIST:
        await message.add_reaction(index_emoji_list[cnt])
        cnt += 1

    # 반응 체크용 메소드
    def check(reaction, user):
        return user == ctx.author and reaction.emoji in index_emoji_list

    # 반응 확인
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30, check=check)
    except asyncio.TimeoutError:
        await ctx.channel.send('취소되었습니다. 😅')
        return
    finally:
        await message.delete()

    # 반응 분석
    user_choice = EmojiNum.emoji_unicode_to(reaction.emoji)
    if user_choice == EmojiNum.UNKNOWN:
        raise Exception('알 수 없는 선택입니다.')
    chosen_cafeteria = CAFETERIA_LIST[user_choice.value - 1]
        
    return chosen_cafeteria


# 문자열 날짜가 델타 날짜(어제/오늘/모레)인지, 요일(월/화/수)인지, 일반타입(YYYY-mm-nn)인지 구별하여 정규화하여 반환함.
def normalize_date(date_str):
    date = datetime(datetime.today().year, datetime.today().month, datetime.today().day, 0, 0, 0, 0, KST)        # 탐색 시간을 일단 오늘로 설정

    if DeltaDay.is_delta_day(date_str):
        delta_day = DeltaDay.str_to(date_str)
        date += timedelta(days=delta_day.value)               # 델타 날짜이면 현재로부터 delta 날짜만큼 조정한다.

    elif DayOfWeek.is_day_of_week(date_str):
        day_of_week = DayOfWeek.str_to(date_str)
        diff = 0 - (date.weekday() - day_of_week.value)
        date += timedelta(days=diff)                          # 요일이면 현재 요일로부터 대상 요일만큼 조정한다.

    else:
        try:
            date = parse(date_str)    # 델타 날짜가 아니라면 일반 날짜(YYYY-mm-dd)로 인식
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
    day_of_week_text = DayOfWeek.int_to_dow(menu._date.weekday()).to_str()
    date_simple_text = menu._date.strftime('%m.%d') + ' (' + day_of_week_text + ')'
    cafe_type_text = '알수없음'
    meal_time_text = menu._meal_time_type.to_str()
    date_full_text = menu._date.strftime('%Y-%m-%d')
    emoji = menu._meal_time_type.to_emoji()

    # 식당이름 enum화
    cafe_type_text = menu._cafe_type.to_str()

    # 메뉴 배열 텍스트화
    menu_elems_txt = ''
    if menu._menu_elems:
        for e in menu._menu_elems:
            menu_elems_txt += e + '\n'
    else:
        menu_elems_txt = '정보 없음'

    # 임베드 생성
    embed = Embed(title=f'{cafe_type_text} {meal_time_text} {emoji} {date_simple_text}',
                  #description=f'{menu_elems_txt}',
                  color=EMBED_COLOR)
    embed.add_field(name='메뉴',value=f'{menu_elems_txt}\n[[링크]]({menu._url})')
    embed.set_footer(text=f'{date_full_text}')
    return embed


# 식당에 알맞는 URL 설정 및 날짜 설정 후 파싱 시도
def parse_zzam(cafeteria_type, date):
    if cafeteria_type is CafeteriaType.UNKNOWN:
        raise Exception('알 수 없는 식당 유형입니다.')
        log(from_text(ctx), 'Unknown Cafeteria Type')

    # 학생식당/교직원식당/분식당별 URL 설정
    URL = CAFETERIA_URL[cafeteria_type.value]

    # URL용 날짜 설정 (찾기 원하는 날짜가 일요일이면 달력이 넘어가서 하루 빼주고 파싱함)
    url_date = date
    if url_date.weekday() is 6:
        url_date -= timedelta(days=1)
    URL += 'mode=menuList&srDt=' + url_date.strftime('%Y-%m-%d')

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
    start_date = parse(start_date_text)

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
        m = Menu(cafeteria_type, menu_date, meal_time_type, menu_elems, url)
        resultArr.append(m)
        cnt += 1

    print('zzam successfully parsed')
    return resultArr


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