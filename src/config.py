from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

DEFAULT_FOCUS_KEYWORDS = [
    "美联储",
    "fed",
    "federal reserve",
    "interest rate",
    "rate hike",
    "rate cut",
    "加息",
    "降息",
    "降准",
    "inflation",
    "cpi",
    "gdp",
    "中国经济",
    "中国股市",
    "a股",
    "上证",
    "港股",
    "stock market",
    "s&p 500",
    "nasdaq",
    "dow jones",
    "原油",
    "crude oil",
    "黄金",
    "gold",
    "commodity",
    "bond",
    "treasury",
    "国债",
    "房地产",
    "real estate",
    "housing",
    "贸易战",
    "tariff",
    "关税",
    "ipo",
    "财报",
    "earnings",
    "央行",
    "central bank",
    "人民币",
    "cny",
    "forex",
    "外汇",
    "财政政策",
    "fiscal policy",
    "monetary policy",
    "量化宽松",
    "quantitative easing",
    "recession",
    "衰退",
]

def _read_bool(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def _read_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return int(raw_value.strip())


def _read_float(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return float(raw_value.strip())


def _resolve_path(base_dir: Path, env_name: str, default: Path) -> Path:
    raw_value = os.getenv(env_name)
    if not raw_value:
        return default

    candidate = Path(raw_value)
    if candidate.is_absolute():
        return candidate
    return (base_dir / candidate).resolve()


def _read_list(name: str, default: list[str]) -> list[str]:
    raw_value = os.getenv(name)
    if raw_value is None or not raw_value.strip():
        return list(default)

    items = [
        item.strip()
        for item in re.split(r"[,，\n\r\t]+", raw_value)
        if item.strip()
    ]
    return items or list(default)


@dataclass(slots=True)
class Settings:
    llm_api_key: str | None
    llm_base_url: str
    llm_model: str
    llm_default_headers: dict[str, str]
    timezone_name: str
    max_articles_per_feed: int
    max_articles_per_run: int
    llm_batch_size: int
    llm_retry_count: int
    max_llm_input_chars_per_article: int
    request_timeout_seconds: int
    llm_batch_timeout_multiplier: float
    user_agent: str
    enable_content_fetch: bool
    allow_fallback_summary: bool
    output_dir: Path
    state_file: Path
    report_title: str
    focus_keywords: list[str]
    blacklist_keywords: list[str]

    @property
    def timezone(self) -> ZoneInfo:
        return ZoneInfo(self.timezone_name)

    @property
    def run_date(self) -> str:
        override = os.getenv("RUN_DATE")
        if override:
            return override
        return datetime.now(self.timezone).date().isoformat()

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_api_key and self.llm_model)


def load_settings(base_dir: Path | None = None) -> Settings:
    root_dir = base_dir or Path(__file__).resolve().parents[1]
    load_dotenv(root_dir / ".env")

    output_dir = _resolve_path(root_dir, "OUTPUT_DIR", root_dir / "data")
    state_file = _resolve_path(root_dir, "STATE_FILE", root_dir / "state" / "seen_urls.json")

    llm_default_headers: dict[str, str] = {}
    referer = os.getenv("OPENROUTER_REFERER")
    app_title = os.getenv("OPENROUTER_TITLE")
    if referer:
        llm_default_headers["HTTP-Referer"] = referer
    if app_title:
        llm_default_headers["X-Title"] = app_title

    return Settings(
        llm_api_key=os.getenv("LLM_API_KEY"),
        llm_base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        timezone_name=os.getenv("TZ_NAME", "Asia/Shanghai"),
        max_articles_per_feed=_read_int("MAX_ARTICLES_PER_FEED", 8),
        max_articles_per_run=_read_int("MAX_ARTICLES_PER_RUN", 50),
        llm_batch_size=_read_int("LLM_BATCH_SIZE", 8),
        llm_retry_count=_read_int("LLM_RETRY_COUNT", 2),
        max_llm_input_chars_per_article=_read_int("MAX_LLM_INPUT_CHARS_PER_ARTICLE", 1800),
        request_timeout_seconds=_read_int("REQUEST_TIMEOUT_SECONDS", 30),
        llm_batch_timeout_multiplier=_read_float("LLM_BATCH_TIMEOUT_MULTIPLIER", 2.5),
        user_agent=os.getenv(
            "REQUEST_USER_AGENT",
            "DailyFinancialNewsBot/1.0 (+https://github.com/<your-github-username>/daily-financial-news)",
        ),
        enable_content_fetch=_read_bool("ENABLE_CONTENT_FETCH", True),
        allow_fallback_summary=_read_bool("ALLOW_FALLBACK_SUMMARY", True),
        output_dir=output_dir,
        state_file=state_file,
        report_title=os.getenv("REPORT_TITLE", "Daily Financial News"),
        focus_keywords=_read_list("FOCUS_KEYWORDS", DEFAULT_FOCUS_KEYWORDS),
        blacklist_keywords=_read_list("BLACKLIST_KEYWORDS", DEFAULT_BLACKLIST_KEYWORDS),
        llm_default_headers=llm_default_headers,
    )
