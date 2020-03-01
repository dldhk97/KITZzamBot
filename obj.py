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

class MealTimeType(enum.Enum):
    BREAKFAST = 0                   # 조식
    LUNCH = 1                       # 중식
    DINNER = 2                      # 석식
    UNKNOWN = -1

    def to_str(meal_time):
        if meal_time is MealTimeType.BREAKFAST:
            return '조식'
        elif meal_time is MealTimeType.LUNCH:
            return '중식'
        elif meal_time is MealTimeType.DINNER:
            return '석식'
        else:
            return '알수없음'

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