import enum

class CafeteriaType(enum.Enum):
    NORM = 0                        # 교내식당
    DORM = 1                        # 기숙사식당
    UNKNOWN = -1

class NormCafeType(enum.Enum):
    STUDENT = 0                     # 학생식당
    STAFF = 1                       # 교직원식당
    SNACKBAR = 2                    # 분식당
    UNKNOWN = -1

    def to_str(type):
        if type is NormCafeType.STUDENT:
            return '학색식당'
        elif type is NormCafeType.STAFF:
            return '교직원식당'
        elif type is NormCafeType.SNACKBAR:
            return '분식당'
        else:
            return '알수없음'

    def get_cafeteria_type():
        return CafeteriaType.NORM

class DormCafeType(enum.Enum):
    PUROOM = 0                      # 푸름관
    OREUM1 = 1                      # 오름관1동
    OREUM3 = 2                      # 오름관3동
    UNKNOWN = -1

    def to_str(type):
        if type is DormCafeType.PUROOM:
            return '푸름관'
        elif type is DormCafeType.OREUM1:
            return '오름관1동'
        elif type is DormCafeType.OREUM3:
            return '오름관3동'
        else:
            return '알수없음'

    def get_cafeteria_type():
        return CafeteriaType.DORM

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
    def __init__(self, cafe_type, cafe_detail_type, date, meal_time_type, menu_elems):
        self._cafe_type = cafe_type
        self._cafe_detail_type = cafe_detail_type
        self._date = date
        self._meal_time_type = meal_time_type
        self._menu_elems = menu_elems

    def cafe_type(self):
        return self._cafe_type

    def cafe_detail_type(self):
        return self._cafe_detail_type

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
        elif str in ['내일', '하루후', '하루뒤']:
            return DeltaDay.TOMORROW
        elif str in ['모레', '이틀후', '글피']:
            return DeltaDay.TDAT
        else:
            return DeltaDay.UNKNOWN