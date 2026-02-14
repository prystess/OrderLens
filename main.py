from fastapi import FastAPI
import requests

# 初始化 FastAPI
app = FastAPI(
    title="OrderLens API",
    description="Fetch Injective orderbook and market data",
    version="0.1"
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
# 基础接口（骨架）
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
