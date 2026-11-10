#!/usr/bin/env python3
"""Build data.js for template-simple.html from real sources.

  - date / 農曆 / moon day ...... lunar-python (offline)
  - rest day or HK holiday ...... HK Government 1823 holiday calendar
  - weather ..................... Hong Kong Observatory open data (fnd = 9-day forecast, rhrread = now)
  - 宜 / 忌 + weather sentence ... simple rule table for now (an LLM can replace this later)

Usage:  python build_data.py [--date YYYY-MM-DD] [--out data.js]
Needs:  pip install lunar-python requests opencc-python-reimplemented
"""
import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from lunar_python import Solar
from opencc import OpenCC

HERE = Path(__file__).resolve().parent
HKT = timezone(timedelta(hours=8))
UA = {"User-Agent": "daily-calendar-hobby/0.1"}
HKO = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php"
HOLIDAYS = "https://www.1823.gov.hk/common/ical/tc.json"
s2hk = OpenCC("s2hk")  # lunar-python outputs Simplified; the calendar is Traditional (HK)

MONTH_CN = ["一月", "二月", "三月", "四月", "五月", "六月",
            "七月", "八月", "九月", "十月", "十一月", "十二月"]

# HKO ForecastIcon code -> template icon (sun | partly | cloud | rain | thunder)
ICON = {50: "sun", 51: "partly", 52: "partly", 53: "rain", 54: "rain",
        60: "cloud", 61: "cloud", 62: "rain", 63: "rain", 64: "rain", 65: "thunder",
        70: "sun", 71: "sun", 72: "sun", 73: "sun", 74: "sun", 75: "sun", 76: "partly", 77: "partly",
        80: "cloud", 81: "sun", 82: "cloud", 83: "cloud", 84: "cloud", 85: "cloud",
        90: "sun", 91: "sun", 92: "cloud", 93: "cloud"}
WORD = {"sun": "天晴", "partly": "晴時多雲", "cloud": "多雲", "rain": "有雨", "thunder": "雷暴"}
WORD_BY_CODE = {81: "天氣乾燥", 82: "天氣潮濕", 83: "有霧", 84: "有薄霧", 85: "有煙霞",
                90: "酷熱", 91: "天氣暖", 92: "天氣清涼", 93: "天氣寒冷"}


def get_json(url, **params):
    r = requests.get(url, params=params or None, headers=UA, timeout=20)
    r.raise_for_status()
    return json.loads(r.content.decode("utf-8-sig"))  # the holiday file starts with a BOM


def lunar_info(d):
    solar = Solar.fromYmd(d.year, d.month, d.day)
    lunar = solar.getLunar()
    month = s2hk.convert(lunar.getMonthInChinese())
    return {
        "weekday": "星期" + solar.getWeekInChinese(),
        "weekday_num": d.isoweekday(),              # 6 = Sat, 7 = Sun
        "lunar_text": f"{month}月{s2hk.convert(lunar.getDayInChinese())}",
        "lunar_day": lunar.getDay(),
        "ganzhi": s2hk.convert(lunar.getYearInGanZhi()) + s2hk.convert(lunar.getYearShengXiao()) + "年",
    }


def day_type(d, weekday_num):
    ymd = d.strftime("%Y%m%d")
    try:
        for ev in get_json(HOLIDAYS)["vcalendar"][0]["vevent"]:
            if ev["dtstart"][0] <= ymd < ev["dtend"][0]:
                return ev["summary"]
    except Exception as e:  # holidays are nice-to-have; fall back to weekday logic
        print(f"warning: holiday lookup failed ({e})", file=sys.stderr)
    return "休息日" if weekday_num >= 6 else "返工日"


def weather(d):
    """Returns dict with forecast (4 days), today's icon/range, humidity. Never raises."""
    out = {"ok": False, "forecast": [["今日", "cloud", None, None]] + [["—", "cloud", None, None]] * 3,
           "icon": "cloud", "code": None, "min": None, "max": None, "psr": "", "temp": None, "rh": None}
    try:
        fnd = get_json(HKO, dataType="fnd", lang="tc")["weatherForecast"]
        now = get_json(HKO, dataType="rhrread", lang="tc")
    except Exception as e:
        print(f"warning: HKO fetch failed ({e}); using placeholders", file=sys.stderr)
        return out

    ymd = d.strftime("%Y%m%d")
    start = next((i for i, f in enumerate(fnd) if f["forecastDate"] == ymd), 0)
    days = fnd[start:start + 4]
    fc = []
    for i, f in enumerate(days):
        label = "今日" if i == 0 else f["week"][-1]
        fc.append([label, ICON.get(f["ForecastIcon"], "cloud"),
                   f["forecastMintemp"]["value"], f["forecastMaxtemp"]["value"]])
    today = days[0]
    pick = lambda items: next((x for x in items if x.get("place") == "香港天文台"), items[0])
    out.update(ok=True, forecast=fc, code=today["ForecastIcon"], icon=ICON.get(today["ForecastIcon"], "cloud"),
               min=today["forecastMintemp"]["value"], max=today["forecastMaxtemp"]["value"], psr=today.get("PSR", ""),
               temp=pick(now["temperature"]["data"])["value"], rh=pick(now["humidity"]["data"])["value"])
    return out


def sayings(w):
    """Rule table for the 宜/忌 lines and the weather sentence (placeholder for an LLM)."""
    mx, mn, icon = w["max"], w["min"], w["icon"]
    rainy = icon in ("rain", "thunder") or w["psr"] in ("中", "中高", "高")
    if mx is None:
        return ["出街行下", "飲杯奶茶"], ["賴床", "遲到"], "暫時未有天氣資料", ""
    if rainy:
        yi, ji, tip = ["帶定遮", "著防水鞋"], ["忘記帶遮", "著白鞋出街"], "出門記得帶遮"
    elif mx >= 31:
        yi, ji, tip = ["開冷氣", "飲杯凍檸茶"], ["正午出街", "著得太厚"], "多飲水，小心中暑"
    elif mx <= 18 or mn <= 14:
        yi, ji, tip = ["著返件褸", "飲杯熱奶茶"], ["短袖出街", "凍親唔講"], "好凍，出街著厚啲"
    elif mx - mn >= 7:
        yi, ji, tip = ["洋蔥式著法", "帶件外套"], ["朝早著短袖", "夜晚凍親"], "朝晚溫差大，帶件外套"
    else:
        yi, ji, tip = ["出街行下", "飲杯奶茶"], ["賴床", "遲到"], "天氣舒適，出街行下"
    word = WORD_BY_CODE.get(w["code"]) or WORD.get(icon, "多雲")
    rh = f"，濕度{w['rh']}%" if w["rh"] is not None else ""
    return yi, ji, f"{word}{rh}", tip


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-MM-DD (default: today in Hong Kong)")
    ap.add_argument("--out", default=str(HERE / "data.js"))
    a = ap.parse_args()

    d = datetime.strptime(a.date, "%Y-%m-%d").date() if a.date else datetime.now(HKT).date()
    li, w = lunar_info(d), weather(d)
    yi, ji, line1, line2 = sayings(w)

    mascot = HERE / "assets" / "cat-wave.png"
    data = {
        "date": d.isoformat(),
        "year": d.year,
        "monthCN": MONTH_CN[d.month - 1],
        "ganzhiShort": li["ganzhi"],
        "day": d.day,
        "dayType": day_type(d, li["weekday_num"]),
        "weekdayCN": li["weekday"],
        "lunarText": li["lunar_text"],
        "lunarDayNum": li["lunar_day"],
        "yiLines": yi,
        "jiLines": ji,
        "forecast": w["forecast"],
        "wxIcon": w["icon"],
        "wxText": line1 + ("\n" + line2 if line2 else ""),
        "weather": {"temp": w["temp"] if w["temp"] is not None else "—"},
        "mascotImg": "assets/cat-wave.png" if mascot.exists() else None,
    }
    Path(a.out).write_text("window.DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
    print(f"wrote {a.out} for {d} (weather {'live' if w['ok'] else 'PLACEHOLDER'})")


if __name__ == "__main__":
    main()
