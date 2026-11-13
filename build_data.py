#!/usr/bin/env python3
"""Build data.js for BOTH template-full.html and template-simple.html from real sources."""
import argparse
import hashlib
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
s2hk = OpenCC("s2hk")

MONTH_CN = ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
MONTH_EN = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
WEEKDAY_EN = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

ICON = {
    50: "sun", 51: "partly", 52: "partly", 53: "rain", 54: "rain",
    60: "cloud", 61: "cloud", 62: "rain", 63: "rain", 64: "rain", 65: "thunder",
    70: "sun", 71: "sun", 72: "sun", 73: "sun", 74: "sun", 75: "sun", 76: "partly", 77: "partly",
    80: "cloud", 81: "sun", 82: "cloud", 83: "cloud", 84: "cloud", 85: "cloud",
    90: "sun", 91: "sun", 92: "cloud", 93: "cloud"
}
WORD = {"sun": "天晴", "partly": "短暫陽光", "cloud": "多雲", "rain": "有雨", "thunder": "雷暴"}
WORD_BY_CODE = {81: "天氣乾燥", 82: "天氣潮濕", 83: "有霧", 84: "有薄霧", 85: "有煙霞", 90: "酷熱", 91: "天氣溫暖", 92: "天氣清涼", 93: "天氣寒冷"}
HK_PLACES = {"正北": "北角", "東北": "沙頭角", "正東": "柴灣", "東南": "將軍澳", "正南": "香港仔", "西南": "大嶼山", "正西": "屯門", "西北": "元朗"}
HOUR_ACTS = [("子", "夜機"), ("丑", "好瞓"), ("寅", "發夢"), ("卯", "晨運"), ("辰", "迫車"), ("巳", "開會"), ("午", "搵食"), ("未", "眼瞓"), ("申", "下午茶"), ("酉", "收工"), ("戌", "晚飯"), ("亥", "煲劇")]


def get_json(url, **params):
    r = requests.get(url, params=params or None, headers=UA, timeout=20)
    r.raise_for_status()
    return json.loads(r.content.decode("utf-8-sig"))


def get_solar_term_info(d):
    lunar = Solar.fromYmd(d.year, d.month, d.day).getLunar()
    prev_jq = lunar.getPrevJieQi(True)
    next_jq = lunar.getNextJieQi(False)
    term_name = s2hk.convert(prev_jq.getName()) if prev_jq else "立冬"
    if next_jq:
        ny = next_jq.getSolar()
        note = f"{ny.getMonth()}月{ny.getDay()}日交{s2hk.convert(next_jq.getName())}"
    else:
        note = "節氣交換"
    return {"name": term_name, "note": note}


def lunar_info(d):
    solar = Solar.fromYmd(d.year, d.month, d.day)
    lunar = solar.getLunar()
    month_str = s2hk.convert(lunar.getMonthInChinese())
    day_str = s2hk.convert(lunar.getDayInChinese())
    ganzhi_yr = s2hk.convert(lunar.getYearInGanZhi())
    zodiac = s2hk.convert(lunar.getYearShengXiao())
    chong_animal = s2hk.convert(lunar.getDayChongShengXiao())
    sha_dir = s2hk.convert(lunar.getDaySha())
    zhixing = s2hk.convert(lunar.getZhiXing())
    pos_cai = s2hk.convert(lunar.getDayPositionCaiDesc())
    pos_xi = s2hk.convert(lunar.getDayPositionXiDesc())
    pos_fu = s2hk.convert(lunar.getDayPositionFuDesc())

    hours_list = []
    for idx, (branch, act) in enumerate(HOUR_ACTS):
        h_solar = Solar.fromYmdHms(d.year, d.month, d.day, (idx * 2) % 24, 30, 0)
        h_luck = s2hk.convert(h_solar.getLunar().getTimeTianShenLuck())
        hours_list.append([branch, act, 1 if h_luck == "吉" else 0])

    seed = int(hashlib.md5(d.isoformat().encode()).hexdigest(), 16)
    luck = [["打工", (seed % 3) + 3], ["財運", ((seed >> 3) % 3) + 3], ["食運", ((seed >> 6) % 3) + 3], ["桃花", ((seed >> 9) % 4) + 2]]

    return {
        "weekday_cn": "星期" + s2hk.convert(solar.getWeekInChinese()),
        "weekday_en": WEEKDAY_EN[d.isoweekday() - 1],
        "weekday_num": d.isoweekday(),
        "ganzhi": f"{ganzhi_yr}年",
        "zodiac": zodiac,
        "ganzhi_short": f"{ganzhi_yr}{zodiac}年",
        "lunar_month": f"{month_str}月",
        "lunar_day_str": day_str,
        "lunar_text": f"{month_str}月{day_str}",
        "lunar_day_num": lunar.getDay(),
        "chong": f"沖肖{chong_animal} · 煞{sha_dir}",
        "zhiri": f"{zhixing}日 · 執生為上",
        "luck": luck,
        "position": [
            [f"財神 · {pos_cai}", HK_PLACES.get(pos_cai, "北角")],
            [f"喜神 · {pos_xi}", HK_PLACES.get(pos_xi, "沙頭角")],
            [f"福神 · {pos_fu}", HK_PLACES.get(pos_fu, "尖沙咀")],
        ],
        "hours": hours_list,
    }


def day_type(d, weekday_num):
    ymd = d.strftime("%Y%m%d")
    try:
        for ev in get_json(HOLIDAYS)["vcalendar"][0]["vevent"]:
            if ev["dtstart"][0] <= ymd < ev["dtend"][0]:
                return ev["summary"]
    except Exception as e:
        print(f"warning: holiday lookup failed ({e})", file=sys.stderr)
    return "休息日" if weekday_num >= 6 else "返工日"


def weather(d):
    out = {"ok": False, "forecast": [["今日", "cloud", 20, 25]] + [["—", "cloud", 20, 25]] * 3, "icon": "cloud", "code": None, "min": 20, "max": 25, "psr": "低", "temp": 24, "rh": 70}
    try:
        fnd = get_json(HKO, dataType="fnd", lang="tc")["weatherForecast"]
        now = get_json(HKO, dataType="rhrread", lang="tc")
    except Exception as e:
        print(f"warning: HKO fetch failed ({e})", file=sys.stderr)
        return out

    ymd = d.strftime("%Y%m%d")
    start = next((i for i, f in enumerate(fnd) if f["forecastDate"] == ymd), 0)
    days = fnd[start:start + 4]
    fc = [["今日" if i == 0 else f["week"][-1], ICON.get(f["ForecastIcon"], "cloud"), f["forecastMintemp"]["value"], f["forecastMaxtemp"]["value"]] for i, f in enumerate(days)]
    today = days[0]
    pick = lambda items: next((x for x in items if x.get("place") == "香港天文台"), items[0])
    out.update(ok=True, forecast=fc, code=today["ForecastIcon"], icon=ICON.get(today["ForecastIcon"], "cloud"), min=today["forecastMintemp"]["value"], max=today["forecastMaxtemp"]["value"], psr=today.get("PSR", "低"), temp=pick(now["temperature"]["data"])["value"], rh=pick(now["humidity"]["data"])["value"])
    return out


def sayings_and_couplets(w, dtype, weekday_cn):
    mx, mn, icon = w["max"], w["min"], w["icon"]
    rainy = icon in ("rain", "thunder") or w["psr"] in ("中", "中高", "高")
    if rainy:
        yi, ji, tip, tagline, couplet_l = ["帶定雨遮", "著防水鞋", "嘆杯熱茶"], ["唔帶雨遮", "著白波鞋", "淋雨感冒"], "出門記得帶遮", "落 雨 濕 濕 · 記 得 帶 遮", "落雨出街記得帶遮"
    elif mx is not None and mx >= 30:
        yi, ji, tip, tagline, couplet_l = ["開大冷氣", "飲凍檸茶", "行商場嘆"], ["正午暴曬", "著得太厚", "心浮氣躁"], "多飲水，小心中暑", "天 氣 炎 熱 · 飲 杯 凍 嘢", "熱到出汗開大冷氣"
    elif (mx is not None and mx <= 19) or (mn is not None and mn <= 15):
        yi, ji, tip, tagline, couplet_l = ["著返件褸", "飲熱奶茶", "夜晚打邊爐"], ["短袖出街", "凍親唔講", "吹風著涼"], "天氣轉涼，出街著厚啲", "涼 風 起 · 著 返 件 褸", "轉涼起風著返件褸"
    else:
        yi, ji, tip, tagline, couplet_l = ["出街行下", "飲杯奶茶", "準時收工"], ["無故賴床", "出門遲到", "捱夜唔瞓"], "秋高氣爽，出街行下", "天 氣 舒 適 · 飲 杯 奶 茶", "東風和暖去飲奶茶"

    couplet_r = "放假休息瞓到唔願起" if dtype != "返工日" else "專心搵食準時收工"
    word = WORD_BY_CODE.get(w["code"]) or WORD.get(icon, "多雲")
    rh = f"，濕度{w['rh']}%" if w["rh"] is not None else ""
    return yi, ji, f"{word}{rh}", tip, tagline, couplet_l, couplet_r


def choose_cat_image(w, dtype):
    rainy = w["icon"] in ("rain", "thunder") or w["psr"] in ("中", "中高", "高")
    cold = (w["max"] is not None and w["max"] <= 19) or (w["min"] is not None and w["min"] <= 15)
    candidates = []
    if rainy:
        candidates.append("assets/cat-rain.png")
    if cold:
        candidates.append("assets/cat-cold.png")
    candidates.append("assets/cat-weekend.png" if dtype != "返工日" else "assets/cat-work.png")
    candidates.append("assets/cat-wave.png")
    for rel in candidates:
        if (HERE / rel).exists():
            return rel
    return "assets/cat-wave.png"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-MM-DD")
    ap.add_argument("--out", default=str(HERE / "data.js"))
    a = ap.parse_args()

    d = datetime.strptime(a.date, "%Y-%m-%d").date() if a.date else datetime.now(HKT).date()
    li = lunar_info(d)
    w = weather(d)
    dtype = day_type(d, li["weekday_num"])
    yi, ji, line1, line2, tagline, couplet_l, couplet_r = sayings_and_couplets(w, dtype, li["weekday_cn"])
    st = get_solar_term_info(d)
    cat_img = choose_cat_image(w, dtype)

    data = {
        "date": d.isoformat(),
        "year": d.year,
        "ganzhi": li["ganzhi"],
        "zodiac": li["zodiac"],
        "ganzhiShort": li["ganzhi_short"],
        "monthCN": MONTH_CN[d.month - 1],
        "monthEN": MONTH_EN[d.month - 1],
        "monthSize": "大" if d.month in (1, 3, 5, 7, 8, 10, 12) else "小",
        "day": d.day,
        "dayType": dtype,
        "weekdayCN": li["weekday_cn"],
        "weekdayEN": li["weekday_en"],
        "tagline": tagline,
        "coupletL": couplet_l,
        "coupletR": couplet_r,
        "solarTerm": st,
        "lunar": {"month": li["lunar_month"], "day": li["lunar_day_str"]},
        "lunarText": li["lunar_text"],
        "lunarDayNum": li["lunar_day_num"],
        "yi": yi,
        "ji": ji,
        "yiLines": yi[:2],
        "jiLines": ji[:2],
        "chong": li["chong"],
        "zhiri": li["zhiri"],
        "luck": li["luck"],
        "position": li["position"],
        "luckyHours": "晨運 · 食宴 · 瞌眼",
        "hours": li["hours"],
        "forecast": w["forecast"],
        "wxIcon": w["icon"],
        "wxText": line1 + ("\n" + line2 if line2 else ""),
        "weather": {"temp": w["temp"], "humidity": w["rh"], "rain": f"降雨{w['psr']}" if w["psr"] else "降雨機會低", "line": line2 or line1},
        "mascotImg": cat_img,
    }
    Path(a.out).write_text("window.DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
    print(f"wrote {a.out} for {d} (cat: {cat_img})")


if __name__ == "__main__":
    main()
