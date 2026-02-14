from fastapi import FastAPI
import requests

# 初始化 FastAPI
app = FastAPI(
    title="OrderLens API",
    description="Fetch Injective orderbook and compute market health metrics",
    version="0.2"
)

# Injective API 基础 URL
INDEXER = "https://api.injective.network"

# -----------------------------
# 数据获取函数
# -----------------------------

def get_orderbook(market_id: str):
    """
    获取指定市场的 orderbook
    """
    url = f"{INDEXER}/api/exchange/spot/v1/markets/{market_id}/orderbook"
    r = requests.get(url)
    return r.json()


def get_markets():
    """
    获取市场列表
    """
    url = f"{INDEXER}/api/exchange/spot/v1/markets"
    r = requests.get(url)
    return r.json()["markets"]

# -----------------------------
# 派生指标函数
# -----------------------------

def compute_microstructure_score(orderbook):
    """
    计算市场微结构指标和健康评分
    """
    bids = orderbook["orderbook"]["bids"]
    asks = orderbook["orderbook"]["asks"]

    if not bids or not asks:
        return {"health_score": 0, "rating": "C"}

    best_bid = float(bids[0]["price"])
    best_ask = float(asks[0]["price"])

    spread = (best_ask - best_bid) / best_bid

    bid_depth = sum(float(b["quantity"]) for b in bids[:10])
    ask_depth = sum(float(a["quantity"]) for a in asks[:10])
    depth = bid_depth + ask_depth

    imbalance = bid_depth / (ask_depth + 1e-9)

    # 健康评分
    score = 100
    if spread > 0.01:
        score -= 25
    if depth < 200:
        score -= 25
    if imbalance > 2 or imbalance < 0.5:
        score -= 15

    # 评级
    if score > 80:
        rating = "A"
    elif score > 60:
        rating = "B"
    else:
        rating = "C"

    return {
        "spread": round(spread, 5),
        "depth": round(depth, 2),
        "imbalance": round(imbalance, 2),
        "health_score": max(score, 0),
        "rating": rating
    }

# -----------------------------
# 基础接口
# -----------------------------

@app.get("/")
def root():
    return {"message": "OrderLens API is running"}


@app.get("/market/orderbook")
def market_orderbook(market_id: str):
    """
    返回指定市场的原始 orderbook
    示例:
    /market/orderbook?market_id=0x0611780ba6960e0b...
    """
    orderbook = get_orderbook(market_id)
    return orderbook


@app.get("/market/list")
def market_list():
    """
    返回市场列表
    """
    markets = get_markets()
    return {"markets": markets}


# -----------------------------
# 派生指标接口
# -----------------------------

@app.get("/market/health")
def market_health(market_id: str):
    """
    返回指定市场的健康评分和指标
    """
    orderbook = get_orderbook(market_id)
    metrics = compute_microstructure_score(orderbook)
    return metrics
