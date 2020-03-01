import enum

class CafeteriaType(enum.Enum):
    STUDENT = 0                     # 학생식당
    STAFF = 1                       # 교직원식당
    SNACKBAR = 2                    # 분식당

    PUROOM = 10                     # 푸름관
    OREUM1 = 11                     # 오름관1동
    OREUM3 = 12                     # 오름관3동

    UNKNOWN = -1

    def to_str(type):
        if type is CafeteriaType.STUDENT:
            return '학색식당'
        elif type is CafeteriaType.STAFF:
            return '교직원식당'
        elif type is CafeteriaType.SNACKBAR:
            return '분식당'
        elif type is CafeteriaType.PUROOM:
            return '푸름관'
        elif type is CafeteriaType.OREUM1:
            return '오름관1동'
        elif type is CafeteriaType.OREUM3:
            return '오름관3동'
        else:
            return '알수없음'

    def str_to(str):
        if str in ['학생식당', '학생', '학식당', '학식', '학']:
            return CafeteriaType.STUDENT
        elif str in ['교직원식당', '교직원', '교식당', '교식', '교']:
            return CafeteriaType.STAFF
        elif str in ['분식당', '분식', '분']:
            return CafeteriaType.SNACKBAR
        elif str in ['푸름관', '푸름', '푸']:
            return CafeteriaType.PUROOM
        elif str in ['오름관1동', '오름1', '오1', '1동']:
            return CafeteriaType.OREUM1
        elif str in ['오름관3동', '오름3', '오3', '3동']:
            return CafeteriaType.OREUM3
        else:
            return CafeteriaType.UNKNOWN

class MealTimeType(enum.Enum):
    BREAKFAST = 0                   # 조식
    LUNCH = 1                       # 중식
    DINNER = 2                      # 석식
    ONECOURSE = 3                   # 일품요리
    UNKNOWN = -1

    def to_str(meal_time):
        if meal_time is MealTimeType.BREAKFAST:
            return '조식'
        elif meal_time is MealTimeType.LUNCH:
            return '중식'
        elif meal_time is MealTimeType.DINNER:
            return '석식'
        elif meal_time is MealTimeType.ONECOURSE:
            return '일품요리'
        else:
            return '알수없음'

    def str_to(str):
        if str in ['조식']:
            return MealTimeType.BREAKFAST
        elif str in ['중식']:
            return MealTimeType.LUNCH
        elif str in ['석식']:
            return MealTimeType.DINNER
        elif str in ['일품요리']:
            return MealTimeType.ONECOURSE
        else:
            return MealTimeType.UNKNOWN

    def to_emoji(meal_time):
        if meal_time is MealTimeType.BREAKFAST:
            return ':sunrise:'
        elif meal_time is MealTimeType.LUNCH:
            return ':sunny:'
        elif meal_time is MealTimeType.DINNER:
            return ':crescent_moon:'
        elif meal_time is MealTimeType.ONECOURSE:
            return ':fork_and_knife:'
        else:
            return ':question:'

class Menu:
    def __init__(self, cafe_type, date, meal_time_type, menu_elems):
        self._cafe_type = cafe_type
        self._date = date
        self._meal_time_type = meal_time_type
        self._menu_elems = menu_elems

    def cafe_type(self):
        return self._cafe_type

    def date(self):
        return self._date

    def meal_time_type(self):
        return self._meal_time_type

    def menu_elems(self):
        return self._menu_elems

class DayOfWeek(enum.Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    UNKNOWN = -1

    def to_str(day):
        if day is DayOfWeek.MONDAY:
            return '월'
        elif day is DayOfWeek.TUESDAY:
            return '화'
        elif day is DayOfWeek.WEDNESDAY:
            return '수'
        elif day is DayOfWeek.THURSDAY:
            return '목'
        elif day is DayOfWeek.FRIDAY:
            return '금'
        elif day is DayOfWeek.SATURDAY:
            return '토'
        elif day is DayOfWeek.SUNDAY:
            return '일'
        else:
            return '알수없음'

    def str_to(str):
        if str in ['월', '월요일']:
            return DayOfWeek.MONDAY
        elif str in ['화', '화요일']:
            return DayOfWeek.TUESDAY
        elif str in ['수', '수요일']:
            return DayOfWeek.WEDNESDAY
        elif str in ['목', '목요일']:
            return DayOfWeek.THURSDAY
        elif str in ['금', '금요일']:
            return DayOfWeek.FRIDAY
        elif str in ['토', '토요일']:
            return DayOfWeek.SATURDAY
        elif str in ['일', '일요일']:
            return DayOfWeek.SUNDAY
        else:
            return DayOfWeek.UNKNOWN

    def int_to_dow(i):
        if i is 0:
            return DayOfWeek.MONDAY
        elif i is 1:
            return DayOfWeek.TUESDAY
        elif i is 2:
            return DayOfWeek.WEDNESDAY
        elif i is 3:
            return DayOfWeek.THURSDAY
        elif i is 4:
            return DayOfWeek.FRIDAY
        elif i is 5:
            return DayOfWeek.SATURDAY
        elif i is 6:
            return DayOfWeek.SUNDAY
        else:
            return DayOfWeek.UNKNOWN

    def is_day_of_week(str):
        if DayOfWeek.str_to(str) is DayOfWeek.UNKNOWN:
            return False
        else:
            return True

class DeltaDay(enum.Enum):
    TDBY = -2               # 그저께 The Day Before Yesterday
    YESTERDAY = -1          # 어제
    TODAY = 0               # 오늘
    TOMORROW = 1            # 내일
    TDAT = 2                # 모레 The Day After Tomorrow
    UNKNOWN = -9


    # 델타 날짜 (오늘/어제/내일/모레)를 enum으로 변환하여 반환
    def str_to(str):
        if str in ['그저께', '이틀전', '엊그제']:
            return DeltaDay.TDBY
        elif str in ['어제', '하루전', '어제께']:
            return DeltaDay.YESTERDAY
        elif str in ['오늘', '지금', '이번']:
            return DeltaDay.TODAY
        elif str in ['내일', '하루후', '하루뒤', '다음날']:
            return DeltaDay.TOMORROW
        elif str in ['모레', '이틀후', '글피', '내일모레', '다다음날']:
            return DeltaDay.TDAT
        else:
            return DeltaDay.UNKNOWN

    def is_delta_day(str):
        if DeltaDay.str_to(str) is DeltaDay.UNKNOWN:
            return False
        else:
            return True