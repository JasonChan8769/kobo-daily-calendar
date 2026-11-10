// MOCK DATA for layout work only. In the real pipeline a script writes this file
// each day (HKO weather + lunar-python 黃曆 fields + LLM-written 港式宜忌 text).
// The 沖煞 / 值日 / 運勢 / 方位 / 吉凶 values below are made up, not real almanac data.
window.DATA = {
  year: 2026,
  ganzhi: "丙午年",
  zodiac: "馬",
  monthCN: "十一月",
  monthEN: "NOVEMBER",
  monthSize: "小",

  day: 11,
  weekdayCN: "星期三",
  weekdayEN: "WEDNESDAY",

  tagline: "涼 風 起 · 著 返 件 褸",
  coupletL: "涼風起著返件褸",
  coupletR: "週三撐過就週末",

  solarTerm: { name: "立冬", note: "11月22日交小雪" },
  lunar: { month: "十月小", day: "初三" },

  yi: ["飲杯熱奶茶", "著返件褸", "夜晚食火鍋"],
  ji: ["短袖出街", "凍親唔識講", "加班"],

  chong: "沖虎 · 煞南",
  zhiri: "滿日 · 滿生為上",
  luck: [
    ["打工", 3], ["財運", 2],
    ["食運", 5], ["桃花", 1]
  ],
  position: [
    ["財神 · 正北", "北角"],
    ["喜神 · 東北", "沙頭角"],
    ["福神 · 正南", "尖沙咀"]
  ],
  luckyHours: "晨運 · 食宴 · 嗑眼",

  hours: [
    ["子", "夜機", 1], ["丑", "好瞓", 0], ["寅", "發夢", 1], ["卯", "晨運", 1],
    ["辰", "擠車", 0], ["巳", "開會", 0], ["午", "搵食", 1], ["未", "眼瞓", 1],
    ["申", "飲茶", 0], ["酉", "收工", 1], ["戌", "晚飯", 0], ["亥", "煲劇", 0]
  ],

  weather: { temp: 24, humidity: 68, rain: "降雨機會低", line: "天氣漸涼，夜晚跌至 20°，出街帶件外套" },

  // ---- fields used by template-simple.html ----
  ganzhiShort: "丙午馬年",
  dayType: "返工日",              // 返工日 / 休息日 / holiday name
  lunarText: "十月初三",
  lunarDayNum: 3,                 // 1-30, drives the moon-phase icon
  yiLines: ["著返件褸", "飲杯熱奶茶"],
  jiLines: ["短袖出街", "凍親唔講"],
  forecast: [                     // [label, icon, low, high]   icon: sun|partly|cloud|rain|thunder
    ["今日", "partly", 21, 26],
    ["四", "sun", 21, 27],
    ["五", "cloud", 22, 26],
    ["六", "rain", 20, 24]
  ],
  wxIcon: "partly",
  wxText: "天氣漸涼，夜晚跌至20°\n出街帶件外套",
  mascotImg: null                 // e.g. "assets/cat-wave.png" once Gemini art exists
};
