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
        days_in_month = {
            1: 31, 2: 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 3: 31,
            4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
        }
        if not (1 <= day <= days_in_month.get(month, 0)):
            return {'success_msg': None, 'error_msg': "輸入格式不正確，請重新輸入，例如: 1990/01/01"}

        self.birthday = {"year": str(year), "month": str(month), "day": str(day)} if year != 0 else {"year": "0", "month": str(month), "day": str(day)}
        birthday_str = f"{year:04d}/{month:02d}/{day:02d}" if year != 0 else f"{month:02d}/{day:02d}"
        return {'success_msg': f"壽星名字叫做 {self.name}，生日是 {birthday_str} 已記錄完成"}