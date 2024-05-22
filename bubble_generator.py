import json
import os

class BubbleGenerator:
    def __init__(self, month_bubble_template_path, star_bubble_template_path):
        self.month_bubble_template_path = month_bubble_template_path
        self.star_bubble_template_path = star_bubble_template_path

    def generate_month_bubble(self, month, birthday_data):
        with open(self.month_bubble_template_path, encoding='utf-8') as f:
            b = json.load(f)

        # 每个月的天数列表，注意2月天数为28，未考虑闰年
        days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        # 修改 Bubble 模板中的標題和日期範圍
        b['body']['contents'][0]['text'] = f"{month}月壽星"
        b['body']['contents'][1]['text'] = f"{month}/1-{month}/{days_in_month[month-1]}"
        # 清空原有的壽星列表
        b['body']['contents'][3]['contents'] = []

        # 筛选并排序指定月份的生日数据 
        #如果要在列表推导式中使用 if ，需要一个表达式来决定每个迭代项如何出现在结果列表中 
        #(name, info) 是每次迭代时添加到列表中的表达式  明确你想从迭代中获取什么，并需要在 for 关键字之前放置
        month_people = [(name, info) for name, info in birthday_data.items() if info['month'] == str(month)]
        
        if not month_people:
            # 如果当月没有寿星，则在Bubble中显示相应信息
            b['body']['contents'][3]['contents'].append({"type": "text", "text": f"這個月沒有人生日", "align": "center"})
        else:
            # 替换 Bubble 模板中的人名和生日
            sorted_month_people = sorted(month_people, key=lambda x: int(x[1]['day']))
            for name, info in sorted_month_people:
                name_text = {"type": "text", "text": name, "size": "lg", "color": "#555555", "flex": 0}
                birthday_text = {"type": "text", "text": f"{info['month']}/{info['day']}", "size": "lg", "color": "#111111", "align": "end"}
                b['body']['contents'][3]['contents'].append(
                    {"type": "box", "layout": "horizontal", "contents": [name_text, birthday_text]}
                )

        return b


    def generate_star_bubble(self,star, birthday_data):
        # 加载 starbubble.json 模板
        with open(self.star_bubble_template_path, encoding='utf-8')
            star_bubble = json.load(f)    
        
        # 获取星座对应的日期范围
        star_date_range = self.get_star_date_range(star)
        
        # 修改 Bubble 模板中的标题和日期范围
        star_bubble['body']['contents'][0]['text'] = f"{star}座"
        star_bubble['body']['contents'][1]['text'] = star_date_range
        
        # 清空原有的生日列表
        star_bubble['body']['contents'][3]['contents'] = []
        
        # 在 birthday_data 中查找指定星座的生日数据
        people_list = {}
        for name, info in birthday_data.items():
            month = int(info['month'])
            day = int(info['day'])
            star_sign = self.get_star_sign(month, day)
            if star_sign == star:
                birthday = f"{info['month']}/{info['day']}"
                people_list[name] = birthday
        
        # 如果有生日数据，则将其添加到 Bubble 模板中
        if people_list:
            for name, birthday in people_list.items():
                name_text = {"type": "text", "text": name, "size": "lg", "color": "#555555", "flex": 0}
                birthday_text = {"type": "text", "text": birthday, "size": "lg", "color": "#111111", "align": "end"}
                star_bubble['body']['contents'][3]['contents'].append(
                    {"type": "box", "layout": "horizontal", "contents": [name_text, birthday_text]}
                )
        else:
            # 如果没有生日数据，则显示提示信息
            star_bubble['body']['contents'][3]['contents'].append(
                {"type": "text", "text": f"此星座沒有人生日", "align": "center"}
            )
        
        return star_bubble

    def get_star_sign(self, month, day): #根据日期返回星座名称
        if (month == 1 and day >= 20) or (month == 2 and day <= 18):
            return "水瓶"
        elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
            return "雙魚"
        elif (month == 3 and day >= 21) or (month == 4 and day <= 19):
            return "牡羊"
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            return "金牛"
        elif (month == 5 and day >= 21) or (month == 6 and day <= 21):
            return "雙子"
        elif (month == 6 and day >= 22) or (month == 7 and day <= 22):
            return "巨蟹"
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            return "獅子"
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            return "處女"
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            return "天秤"
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            return "天蠍"
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            return "射手"
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            return "魔羯"
        else:
            return None

    def get_star_date_range(self, star): #根據星座返回星座的日期范围
        star_date_ranges = {
            "水瓶": "1/20-2/18",
            "雙魚": "2/19-3/20",
            "牡羊": "3/21-4/19",
            "金牛": "4/20-5/20",
            "雙子": "5/21-6/21",
            "巨蟹": "6/22-7/22",
            "獅子": "7/23-8/22",
            "處女": "8/23-9/22",
            "天秤": "9/23-10/22",
            "天蠍": "10/23-11/21",
            "射手": "11/22-12/21",
            "魔羯": "12/22-1/19"
        }
        return star_date_ranges.get(star, "未知星座")