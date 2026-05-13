# Digital Oracle — 新数据源迭代计划

## 产品定位

Digital Oracle 的核心哲学：**"所有公开信息都已经被价格消化了。一切信息都在 K 线里。"**

新数据源的标准：
- 必须是**真金白银的市场交易数据**（价格、利差、波动率、持仓量），不是观点/预测/投票
- 必须是**结构化 API**，不是需要 web search 碰运气的数据
- 优先**零外部依赖**（纯 Python stdlib + urllib）
- 遵循项目现有的 provider 模式（见下方规范）

---

## 项目代码规范

### Provider 模式

所有 provider 必须遵循的模式（参考 `bis.py`, `cftc.py` 等现有实现）：

1. **继承 `SignalProvider` 基类**（`from .base import SignalProvider`）
2. **依赖注入 HTTP 客户端**：构造函数接受可选的 `http_client` 参数，默认用 `UrllibJsonClient()`
3. **Query 用 `@dataclass(frozen=True)`**，Result 用 `@dataclass` 或 `@dataclass(frozen=True)`
4. **数值解析用 `_coerce_float()` / `_coerce_int()`**（从 `._coerce` 导入）
5. **错误用 `ProviderParseError`**（从 `.base` 导入）
6. **文件放 `digital_oracle/providers/` 目录下**

### HTTP 客户端

项目提供 `UrllibJsonClient`（`digital_oracle/http.py`），支持：
- `get_json(url, params={...})` — 返回解析后的 JSON
- `get_text(url, params={...})` — 返回原始文本（用于 CSV）
- 自带重试（3 次）和超时（20 秒）
- 重要：使用 `Mapping[str, object]` 作为 params 类型，值为 `None` 的参数会被自动过滤

### 测试规范

每个 provider 有对应的 `tests/test_{name}_provider.py`：
- 使用 `unittest.TestCase`
- 用 **Fake HTTP Client** 注入预设响应（不做真实网络请求）
- 测试正常解析、空响应、异常数据等情况
- 参考 `tests/test_bis_provider.py` 的模式

### 导出规范

新 provider 的 Query 和 Result 类型必须在以下位置注册导出：
1. `digital_oracle/providers/__init__.py` — import 并加入 `__all__`
2. `digital_oracle/__init__.py` — import 并加入 `__all__`

### 文档规范

- `references/providers.md` — 添加 API 速查章节
- `SKILL.md` — 在 Step 2 信号菜单和 Step 4 代码示例中引用

---

## 实施状态总览

| 状态 | Provider | 迭代 | 完成日期 |
|------|----------|------|----------|
| 🔴 待实施 | FredProvider | 迭代 1 | - |
| 🟢 已完成 | FearGreedProvider | 迭代 2 | 2026-04 |
| 🟢 已完成 | CMEFedWatchProvider | 迭代 3 | 2026-04 |
| 🟢 已完成 | 概率合成模块 | 迭代 4 | 2026-04 |
| 🟢 已完成 | 信号质量评估框架 | 迭代 5 | 2026-04 |
| 🟢 已完成 | Provider 能力增强 | 迭代 6 | 2026-05 |

### 已完成但未在原计划中的实施项

以下功能模块在开发过程中超出原计划范围，已全部实施并集成到 SKILL.md 和 providers.md 中：

- **`combination.py`**：`linear_pool()` 和 `logarithmic_pool()` 概率合成工具，含置信度评分
- **`signal_quality.py`**：`SignalQuality` 评估框架 + `PROBABILITY_PHYSICAL` / `PROBABILITY_RISK_NEUTRAL` / `PROBABILITY_NAIVE_MIDPOINT` 概率测度分类
- **EdgarProvider `search_filings()`**：SEC 全文关键词检索（表格类型/日期过滤）
- **BisProvider `get_credit_to_gdp()`**：信贷/GDP 缺口指标
- **CoinGeckoProvider `get_global()` + `list_markets()`**：全球市场概览 + 市值排名
- **USTreasuryProvider `list_exchange_rates()`**：财政部财政汇率数据
- **CftcCotProvider 计算属性**：`mm_net`, `prod_net`, `smart_money_direction`, `commercial_hedge_intensity`, `speculative_ratio`
- **WebSearchProvider 增强**：全局限频（2s 间隔）、CAPTCHA 检测与退避重试、`fetch_page()` 页面抓取、`WebSearchQuery` 结构化查询
- **YFinanceProvider `iv_skew()`**：IV 偏斜分析
- **DeribitProvider `get_option_chain()`**：期权链（含 mark_iv）
- **PolymarketProvider `tag_slug` + `title_contains`**：增强搜索过滤
- **StooqProvider** — 向后兼容包装器，委托给 `YahooPriceProvider`

---

## 迭代 1：FredProvider（FRED 美联储经济数据库）🔴 待实施

### 为什么

现在 VIX、高收益债利差（OAS）、MOVE 指数、利差等关键市场价格数据全靠 web search 获取，不稳定且不结构化。FRED 提供 84 万条时间序列，覆盖利率、利差、波动率等核心价格信号。

### API 概要

- Base URL: `https://api.stlouisfed.org/fred`
- 认证: 需要免费 API key（注册 https://fredaccount.stlouisfed.org/apikeys ）
- 格式: JSON
- 无外部依赖

### 需要实现的方法

#### 1. `get_series(query: FredSeriesQuery) -> FredSeries`

获取一条时间序列的数据点。

```python
@dataclass(frozen=True)
class FredSeriesQuery:
    series_id: str              # e.g. "VIXCLS", "BAMLH0A0HYM2"
    observation_start: str | None = None  # YYYY-MM-DD
    observation_end: str | None = None    # YYYY-MM-DD
    limit: int | None = None
    sort_order: str = "desc"    # "asc" or "desc"

@dataclass(frozen=True)
class FredObservation:
    date: str       # YYYY-MM-DD
    value: float

@dataclass
class FredSeries:
    series_id: str
    title: str | None
    frequency: str | None          # e.g. "Daily", "Monthly"
    units: str | None              # e.g. "Percent", "Index"
    observations: tuple[FredObservation, ...]
```

API endpoint: `GET /fred/series/observations`
- params: `series_id`, `api_key`, `file_type=json`, `observation_start`, `observation_end`, `limit`, `sort_order`
- 返回 JSON: `{"observations": [{"date": "2026-04-10", "value": "19.23"}, ...]}`
- 注意: value 为字符串，"." 表示缺失值，需要过滤

#### 2. `search_series(query: FredSearchQuery) -> list[FredSeriesInfo]`

按关键词搜索序列。

```python
@dataclass(frozen=True)
class FredSearchQuery:
    search_text: str
    limit: int = 20

@dataclass(frozen=True)
class FredSeriesInfo:
    series_id: str
    title: str
    frequency: str | None
    units: str | None
    observation_start: str | None
    observation_end: str | None
    popularity: int | None
```

API endpoint: `GET /fred/series/search`
- params: `search_text`, `api_key`, `file_type=json`, `limit`

### Provider 构造

```python
class FredProvider(SignalProvider):
    provider_id = "fred"
    display_name = "FRED (Federal Reserve Economic Data)"
    capabilities = ("economic_series", "series_search")

    def __init__(self, api_key: str, http_client: FredHttpClient | None = None):
        self.api_key = api_key
        self.http_client = http_client or UrllibJsonClient()
```

注意: `api_key` 是必传参数（FRED 要求认证）。

### SKILL.md 集成

在 Step 2 信号菜单中将以下 web search 项替换为 FRED：

| 原来（web search） | 替换为（FRED series_id） |
|---|---|
| "VIX index current" | `VIXCLS` (CBOE Volatility Index) |
| "US high yield OAS spread" | `BAMLH0A0HYM2` (ICE BofA US High Yield OAS) |
| "MOVE index" | `MOVE` (ICE BofAML MOVE Index)  |
| 10Y-2Y spread | `T10Y2Y` (10-Year minus 2-Year Treasury) |
| TED spread | `TEDRATE` |
| Margin debt | `BOGZ1FL663067003Q` |
| US breakeven inflation | `T10YIE` (10-Year Breakeven Inflation) |
| Initial jobless claims | `ICSA` |
| US CPI | `CPIAUCSL` |

在 gather 示例中添加:
```python
fred = FredProvider(api_key="YOUR_FRED_API_KEY")  # free at https://fredaccount.stlouisfed.org/apikeys

result = gather({
    # ... existing providers ...
    "vix": lambda: fred.get_series(FredSeriesQuery(series_id="VIXCLS", limit=30)),
    "hy_spread": lambda: fred.get_series(FredSeriesQuery(series_id="BAMLH0A0HYM2", limit=30)),
    "move": lambda: fred.get_series(FredSeriesQuery(series_id="MOVE", limit=30)),
    "t10y2y": lambda: fred.get_series(FredSeriesQuery(series_id="T10Y2Y", limit=30)),
})
```

### 测试要求

在 `tests/test_fred_provider.py` 中：

```python
SAMPLE_OBSERVATIONS_JSON = {
    "observations": [
        {"date": "2026-04-10", "value": "19.23"},
        {"date": "2026-04-09", "value": "21.05"},
        {"date": "2026-04-08", "value": "."},      # missing value, should be skipped
    ]
}

SAMPLE_SEARCH_JSON = {
    "seriess": [
        {
            "id": "VIXCLS",
            "title": "CBOE Volatility Index: VIX",
            "frequency": "Daily",
            "units": "Index",
            "observation_start": "1990-01-02",
            "observation_end": "2026-04-10",
            "popularity": 95,
        }
    ]
}
```

测试用例：
1. 正常解析 observations（含跳过 "." 缺失值）
2. 空 observations 返回空 tuple
3. search_series 正常解析
4. 验证 api_key 被传入请求参数
5. limit 和 sort_order 参数传递正确

---

## 迭代 2：FearGreedProvider（CNN Fear & Greed Index）🟢 已完成

### 为什么

CNN Fear & Greed Index 是一个**完全基于市场交易数据衍生**的综合情绪指标，由 7 个价格信号加权合成：
1. 股票价格动量（S&P 500 vs 125 日均线）
2. 股票价格强度（52 周新高 vs 新低）
3. 股票价格波幅（VIX）
4. Put/Call 期权比率
5. 垃圾债需求（高收益债 vs 投资级利差）
6. 市场波动率（VIX 偏离度）
7. 避险需求（股票 vs 债券收益率差）

**它不是观点聚合，是 7 个价格信号的合成**，完全符合 Digital Oracle 的产品哲学。

### 实施摘要

- **文件：** `digital_oracle/providers/fear_greed.py`
- **API 端点：** `https://production.dataviz.cnn.io/index/fearandgreed/graphdata`
- **零外部依赖 + 零 API key**
- **返回：** `FearGreedSnapshot` — score (0-100)、rating、timestamp、previous_close、one_week_ago、one_month_ago、one_year_ago
- **解析亮点：** CNN API 返回 `{"fear_and_greed": {"score": ..., "rating": ...}, "fear_and_greed_historical": {...}}` 嵌套结构，provider 正确处理了两种格式（顶层和嵌套）
- **SKILL.md 集成：** ✅ Step 2 所有分类 + provider 表格 + Step 4 代码示例 + Notes
- **providers.md 集成：** ✅ 完整 API 速查章节
- **测试：** ✅ `tests/test_fear_greed_provider.py`，覆盖正常/极端/缺失响应

---

## 迭代 3：CMEFedWatchProvider（利率期货隐含概率）🟢 已完成

### 为什么

"美联储下次会加息还是降息？" 是宏观分析中最常见的问题之一。用 30 天联邦基金利率期货的价格可以直接计算出市场隐含的利率概率——"价格即共识"的经典场景。

### 实施摘要

- **文件：** `digital_oracle/providers/cme_fedwatch.py`
- **API 端点：** CME 官方 JSON endpoint ← 实际实现中无需 FRED 备选方案
- **零外部依赖 + 零 API key**
- **返回：** `list[FedMeetingProbability]` — 每次 FOMC 会议的利率目标范围 + 概率分布
- **解析亮点：** 响应解析能处理多种 JSON 格式（list、嵌套 object、snake_case/camelCase），韧性高
- **SKILL.md 集成：** ✅ Step 2 "Economic recession / Macro cycle" + provider 表格 + Step 4 代码示例 + Notes
- **providers.md 集成：** ✅ 完整 API 速查章节 + Kalshi KXFED 备选方案说明
- **测试：** ✅ `tests/test_cme_fedwatch_provider.py`

---

## 迭代 4：概率合成模块 (combination.py) 🟢 已完成

在 Step 5 分析阶段，AI 需要将多个来源的概率合成为一个估计值。

- **`linear_pool()`**：加权平均，返回合成概率 + 置信度评分
- **`logarithmic_pool()`**：几何平均赔率比，天然抑制离散信号（满足外部性公理）
- **导出：** `from digital_oracle import linear_pool, logarithmic_pool`

---

## 迭代 5：信号质量评估框架 (signal_quality.py) 🟢 已完成

为每个信号标注可靠性和概率测度类型，帮助 AI 判断信号权重。

- **`SignalQuality`**：流动性等级 (high/medium/low)、数据新鲜度（staleness_hours）、更新频率
- **概率测度常量：** `PROBABILITY_PHYSICAL`、`PROBABILITY_RISK_NEUTRAL`、`PROBABILITY_NAIVE_MIDPOINT`
- **便捷属性：** `is_fresh`（按频率阈值判断）、`is_reliable`（高/中流动性 + 新鲜）

---

## 迭代 6：Provider 能力增强 🟢 已完成

对现有 provider 的扩能，每个增强已完整集成到 SKILL.md 和 providers.md。

| Provider | 增强内容 |
|----------|----------|
| EdgarProvider | `search_filings(EdgarSearchQuery(...))`：SEC 全文关键词检索，支持表格类型 + 日期过滤 |
| BisProvider | `get_credit_to_gdp(BisCreditGapQuery(...))`：信贷/GDP 缺口，gap_pct > 10 = BIS 阈值警告 |
| CoinGeckoProvider | `get_global()`（全球总市值/BTC/ETH 主导率）+ `list_markets()`（市值排名） |
| USTreasuryProvider | `list_exchange_rates(ExchangeRateQuery(...))`：财政部汇率数据，含 `record_date_gte/lte` 过滤 |
| CftcCotProvider | 计算属性：`mm_net`、`prod_net`、`smart_money_direction`、`commercial_hedge_intensity`、`speculative_ratio` |
| WebSearchProvider | 全局限频（2s 间隔，全局锁）、CAPTCHA 检测与退避重试（3次，3/6/9s）、`fetch_page(WebPageQuery(...))`、结构化 `WebSearchQuery` |
| YFinanceProvider | `iv_skew(delta_target=0.25)`：OTM put - OTM call IV，正=下行恐惧溢价 |
| DeribitProvider | `get_option_chain(DeribitOptionChainQuery(...))`：含 `mark_iv`、`atm_strike()`、book summaries |
| PolymarketProvider | `tag_slug` 服务端标签过滤 + `title_contains` 客户端标题过滤 + `get_event()` 按 slug 获取 |
| StooqProvider | 向后兼容包装器：自动映射传统 Stooq 符号 → Yahoo Finance 符号，内部委托给 `YahooPriceProvider` |

---

## 迭代顺序和优先级（更新后）

| 优先级 | Provider | 状态 | 依赖 | 理由 |
|--------|----------|------|------|------|
| **P0** | FredProvider | 🔴 待实施 | stdlib（需 API key） | 一举替换最多的 web search 补丁，覆盖 VIX/OAS/MOVE/利差 |
| ~~P1~~ | FearGreedProvider | 🟢 已完成 | stdlib | 10 分钟搞定，免费无 key，7 个价格信号的合成情绪指标 |
| ~~P2~~ | CMEFedWatchProvider | 🟢 已完成 | stdlib | 利率概率是宏观分析的核心 |
| - | 概率合成 + 信号质量 | 🟢 已完成 | stdlib | 分析工具链完整性 |
| - | Provider 能力增强 | 🟢 已完成 | stdlib + yfinance | 深度挖掘现有 provider 的价值 |
```

## 每完成一个迭代后 checklist

1. ✅/❌ 添加 provider 代码 + 测试
2. ✅/❌ 在 `providers/__init__.py` 和 `__init__.py` 注册导出
3. ✅/❌ 更新 `SKILL.md`（Step 2 信号菜单 + Step 4 代码示例 + provider 表 + Notes）
4. ✅/❌ 更新 `references/providers.md`
5. ✅/❌ 运行 `pytest tests/ -x -q` 确保全部通过

> 当前待实施：仅 **FredProvider**（P0）。所有其他迭代已全部完成并通过验证。