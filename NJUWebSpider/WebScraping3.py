import requests

# 替换为你的和风天气 API Key
API_KEY = "7ff840a9ed384e6799ea9d029ded5b6f"
LOCATION_ID = "101190104"  # 南京市鼓楼区（中国天气网编码）


def get_nanjing_weather():
    url = f"https://devapi.qweather.com/v7/weather/7d?location={LOCATION_ID}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["code"] != "200":
        print("请求失败:", data.get("message", "未知错误"))
        return

    print("南京市鼓楼区未来7天天气预报：")
    for day in data["daily"]:
        date = day["fxDate"]
        temp_min = day["tempMin"]
        temp_max = day["tempMax"]
        precipitation = day.get("precip", "N/A")  # 降水量（mm）
        text_day = day["textDay"]  # 白天天气描述
        text_night = day["textNight"]  # 夜间天气描述

        print(f"{date} | 气温: {temp_min}°C ~ {temp_max}°C | 降水: {precipitation}mm | 天气: {text_day}/{text_night}")


if __name__ == "__main__":
    get_nanjing_weather()