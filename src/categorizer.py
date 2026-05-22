from __future__ import annotations

import re

from .models import ArticleSummary

CATEGORY_RULES: list[tuple[str, list[str]]] = [
    (
        "股市",
        [
            "stock market",
            "stock",
            "equity",
            "shares",
            "s&p 500",
            "nasdaq",
            "dow jones",
            "a股",
            "股市",
            "上证",
            "深证",
            "创业板",
            "港股",
            "日经",
            "牛熊",
            "大盘",
            "股指",
        ],
    ),
    (
        "债市",
        [
            "bond",
            "treasury yield",
            "国债",
            "债券",
            "收益率曲线",
            "信用债",
            "城投债",
            "利率债",
            "可转债",
        ],
    ),
    (
        "大宗商品",
        [
            "commodity",
            "crude oil",
            "gold",
            "silver",
            "copper",
            "iron ore",
            "农产品",
            "期货",
            "原油",
            "黄金",
            "铁矿石",
            "螺纹钢",
        ],
    ),
    (
        "楼市与房地产",
        [
            "real estate",
            "housing",
            "mortgage",
            "property",
            "楼市",
            "房地产",
            "房贷",
            "房价",
            "土地",
            "房企",
        ],
    ),
    (
        "宏观经济",
        [
            "gdp",
            "cpi",
            "inflation",
            "deflation",
            "ppi",
            "pmi",
            "经济数据",
            "宏观经济",
            "经济增长",
            "就业",
            "失业率",
            "消费",
            "零售",
            "固定资产投资",
        ],
    ),
    (
        "央行与货币政策",
        [
            "central bank",
            "federal reserve",
            "fed",
            "interest rate",
            "rate hike",
            "rate cut",
            "monetary policy",
            "quantitative easing",
            "央行",
            "美联储",
            "加息",
            "降息",
            "降准",
            "mlf",
            "lpr",
            "逆回购",
        ],
    ),
    (
        "外汇市场",
        [
            "forex",
            "fx",
            "exchange rate",
            "usd",
            "cny",
            "人民币",
            "美元指数",
            "汇率",
            "贬值",
            "升值",
            "外汇",
        ],
    ),
    (
        "公司财报与IPO",
        [
            "earnings",
            "revenue",
            "profit",
            "quarterly results",
            "ipo",
            "财报",
            "营收",
            "净利润",
            "上市",
            "盈警",
            "业绩",
        ],
    ),
    (
        "监管与合规",
        [
            "regulation",
            "sec",
            "antitrust",
            "regulatory",
            "compliance",
            "监管",
            "合规",
            "反垄断",
            "处罚",
            "罚款",
            "退市",
        ],
    ),
    (
        "国际财经",
        [
            "trade war",
            "tariff",
            "sanction",
            "geopolitics",
            "贸易战",
            "关税",
            "制裁",
            "opec",
            "欧盟",
            "一带一路",
        ],
    ),
    (
        "科技与创新",
        [
            "ai",
            "artificial intelligence",
            "semiconductor",
            "chip",
            "blockchain",
            "fintech",
            "科技",
            "人工智能",
            "半导体",
            "芯片",
            "新能源",
            "电动汽车",
        ],
    ),
    (
        "基金与理财",
        [
            "fund",
            "etf",
            "mutual fund",
            "wealth management",
            "基金",
            "理财",
            "私募",
            "公募",
            "资管",
            "信托",
        ],
    ),
    (
        "能源与资源",
        [
            "energy",
            "renewable",
            "solar",
            "wind power",
            "natural gas",
            "coal",
            "能源",
            "新能源",
            "光伏",
            "风电",
            "锂",
            "电池",
        ],
    ),
]
CATEGORY_LABELS_EN = {
    "股市": "Stock Markets",
    "债市": "Bond Markets",
    "大宗商品": "Commodities",
    "楼市与房地产": "Real Estate & Housing",
    "宏观经济": "Macroeconomics",
    "央行与货币政策": "Central Bank & Monetary Policy",
    "外汇市场": "Forex",
    "公司财报与IPO": "Earnings & IPO",
    "监管与合规": "Regulation & Compliance",
    "国际财经": "International Finance",
    "科技与创新": "Technology & Innovation",
    "基金与理财": "Funds & Wealth Management",
    "能源与资源": "Energy & Resources",
    "综合资讯": "General News",
}
DEFAULT_CATEGORY = "综合资讯"


def categorize_summary(summary: ArticleSummary) -> str:
    normalized_summary = summary.summary.replace("未调用大模型，以下为原文关键信息摘录：", "")
    search_text = "\n".join(
        [
            summary.title_zh or summary.title,
            summary.title,
            summary.source,
            normalized_summary,
            " ".join(summary.keywords),
            " ".join(summary.important_points),
            " ".join(summary.matched_focus_keywords),
        ]
    )

    for category, keywords in CATEGORY_RULES:
        if any(_contains_keyword(search_text, keyword) for keyword in keywords):
            return category
    return DEFAULT_CATEGORY


def format_category_label(category: str) -> str:
    english = CATEGORY_LABELS_EN.get(category, "")
    if not english:
        return category
    return f"{category} / {english}"


def _contains_keyword(text: str, keyword: str) -> bool:
    cleaned_keyword = keyword.strip()
    if not cleaned_keyword:
        return False

    if re.search(r"[\u4e00-\u9fff]", cleaned_keyword):
        return cleaned_keyword in text

    pattern = re.compile(
        rf"(?<![A-Za-z0-9]){re.escape(cleaned_keyword)}(?![A-Za-z0-9])",
        re.IGNORECASE,
    )
    return bool(pattern.search(text))
