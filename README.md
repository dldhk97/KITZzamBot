# KIT 짬봇 for Discord
금오공과대학교 식사 메뉴를 디스코드에서 볼 수 있게 하는 봇입니다.

## Demo
[봇 초대 링크](https://discordapp.com/oauth2/authorize?client_id=683609253575131157&scope=bot&permissions=101440)

Heroku 무료 Dyno에서 테스트용으로 돌아가고 있는 봇입니다. 사용자가 몰리면 봇 응답이 느려지거나 봇이 꺼질 수 있으며, 예고 없이 봇 작동이 중지될 수 있습니다. 

## 설치 및 실행
```
$ pip3 install -r requirements.txt
env_example.txt 참고하여 .env 파일 생성 후, BOT_TOKEN에 봇 토큰 입력
.env 파일 내 옵션들 수정 가능함(PREFIX)
$ python3 main.py
```

## 사용법
$짬 [식당명] [옵션-날짜]

사용 예시 : $짬 학생식당 오늘, $짬 학식, $짬 분식 수요일

봇 초대 후 "$도움" 으로 사용법을 확인할 수 있습니다.

사용가능한 식당명 : 학생식당, 교직원식당, 분식당, 푸름관, 오름관1동, 오름관3동

식당명 축약어도 사용가능. ex) 학생식당->학식, 학식당 / 오름관3동->오름3, 오3, 3동 ...
    
    날짜는 요일/어제오늘/날짜값 사용가능. 

    ex1) 화요일, 토요일 ...
    ex2) 어제, 오늘, 내일, 모레, 이틀전, 이틀후, 엊그제, 다다음날 ...
    ex3) 2020-03-01, 2020.01.01, ...

## TODO
* 특정 시간마다 식사 메뉴 알림
* 리팩토링

impressed by [dccon hassan](https://github.com/Dogdriip/dccon_hassan).
