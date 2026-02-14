from fastapi import FastAPI
import requests

# 初始化 FastAPI
app = FastAPI(
    title="OrderLens API",
    description="Fetch Injective orderbook, compute market health metrics, and rank markets",
    version="0.3"
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


# -----------------------------
# 排名接口（Top Healthy Markets）
# -----------------------------

@app.get("/market/top-healthy")
def top_healthy_markets(limit: int = 5):
    """
    返回健康评分最高的前 N 个市场
    """
    markets = get_markets()
    ranked_markets = []

    # 避免请求过多，只取前20个市场计算
    for m in markets[:20]:
        market_id = m["marketId"]
        try:
            orderbook = get_orderbook(market_id)
            metrics = compute_microstructure_score(orderbook)
            ranked_markets.append({
                "market": m["ticker"],
                "health_score": metrics["health_score"],
                "rating": metrics["rating"]
            })
        except Exception as e:
            print(f"Error fetching {m['ticker']}: {e}")
            continue

    # 排序
    ranked_markets.sort(key=lambda x: x["health_score"], reverse=True)

    return ranked_markets[:limit]
