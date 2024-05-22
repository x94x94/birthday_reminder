class Person:
    def __init__(self, name):
        self.name = name
        self.birthday = None

    def show(self):
        print(f"{self.name} {self.birthday}")
    
    def setBirthday(self, birthday_parts_text):
        birthday_parts = birthday_parts_text.split('/')
        year, month, day = 0, 0, 0

        # 判斷邏輯
        if len(birthday_parts) == 3:
            year, month, day = map(int, birthday_parts)
        elif len(birthday_parts) == 2:
            month, day = map(int, birthday_parts)
        else:
            return {'success_msg': None, 'error_msg': "輸入格式不正確，請重新輸入，例如: 1990/01/01"}
   
        # 1. 檢查年
        if year != 0 and (2024 < year or year < 1900):
            return {'success_msg': None, 'error_msg': "輸入格式不正確，請重新輸入，例如: 1990/01/01"}
        # 2. 檢查月
        if not (1 <= month <= 12):
            return {'success_msg': None, 'error_msg': "輸入格式不正確，請重新輸入，例如: 1990/01/01"}
        # 3. 檢查日
        if month in [1, 3, 5, 7, 8, 10, 12]:
            if not (1 <= day <= 31):
                return {'success_msg': None, 'error_msg': "輸入格式不正確，請重新輸入，例如: 1990/01/01"}
        elif month in [4, 6, 9, 11]:
            if not (1 <= day <= 30):
                return {'success_msg': None, 'error_msg': "輸入格式不正確，請重新輸入，例如: 1990/01/01"}
        elif month == 2:
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):  # 閏年
                if not (1 <= day <= 29):
                    return {'success_msg': None, 'error_msg': "輸入格式不正確，請重新輸入，例如: 1990/01/01"}
            else:
                if not (1 <= day <= 28):
                    return {'success_msg': None, 'error_msg': "輸入格式不正確，請重新輸入，例如: 1990/01/01"}


        if year != 0:
            self.birthday = {"year": str(year), "month": str(month), "day": str(day)}
        else:
            self.birthday = {"year": "0", "month": str(month), "day": str(day)}

        if year != 0:
            return {'success_msg': f"壽星名字叫做 {self.name}，生日是 {year:04d}/{month:02d}/{day:02d} 已記錄完成"}
        else:
            return {'success_msg': f"壽星名字叫做 {self.name}，生日是 {month:02d}/{day:02d} 已記錄完成"}