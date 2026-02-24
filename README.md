OrderLens

OrderLens is a lightweight REST API that converts raw orderbook data from Injective into structured market intelligence.

Instead of returning raw exchange data, OrderLens computes actionable market metrics such as spread, liquidity depth, imbalance, and a simplified health score.

🚀 What This API Does

OrderLens transforms low-level orderbook data into:

Market health score (0–100)

Liquidity depth estimation

Bid/ask imbalance

Market ranking

Simple BUY / SELL / NEUTRAL signal

It is designed for:

Trading dashboards

Quant bots

Market monitoring tools

Developer experimentation

🧠 Core Features
1️⃣ Market Health Scoring

Evaluates a market based on:

Spread percentage

Top 10 level liquidity depth

Orderbook imbalance

Returns a numerical score and rating (A / B / C).

2️⃣ Market Ranking

Ranks markets by computed health score.

Helps identify:

Liquid markets

Stable trading pairs

Thin or unstable markets

3️⃣ Trade Signal Endpoint

Provides a simplified directional signal:

BUY

SELL

NEUTRAL

Based on:

Health score

Orderbook imbalance

📡 API Endpoints
GET /

Basic health check.

Response:

{
  "message": "OrderLens API is running"
}
GET /market/health

Parameters:

Parameter	Type	Required
market_id	string	yes

Example:

/market/health?market_id=YOUR_MARKET_ID

Response:

{
  "spread": 0.0021,
  "depth": 342.55,
  "imbalance": 1.23,
  "health_score": 88,
  "rating": "A"
}
GET /market/top-healthy

Parameters:

Parameter	Type	Required
limit	int	no

Example:

/market/top-healthy?limit=5

Returns top ranked markets by health score.

GET /market/signal

Parameters:

Parameter	Type	Required
market_id	string	yes

Example:

/market/signal?market_id=YOUR_MARKET_ID

Response:

{
  "market": "0x...",
  "health_score": 92,
  "rating": "A",
  "signal": "BUY"
}
🔗 Injective Data Used

OrderLens consumes live data from the Injective public indexer API:

Spot market list

Spot orderbook

Bid/ask depth

Price levels

No private keys required.
No trading execution performed.
Read-only analytics layer.

🛠 How to Run Locally
1️⃣ Clone repository
git clone https://github.com/prystess/OrderLens.git
cd OrderLens
2️⃣ Create virtual environment
python -m venv venv

Activate:

Windows:

venv\Scripts\activate

Mac/Linux:

source venv/bin/activate
3️⃣ Install dependencies
pip install fastapi uvicorn requests
4️⃣ Run the server
uvicorn main:app --reload

You should see:

Uvicorn running on http://127.0.0.1:8000
📞 How to Call the API

Open browser:

http://127.0.0.1:8000/docs

Interactive Swagger UI will appear.

Or call via curl:

curl "http://127.0.0.1:8000/market/health?market_id=YOUR_MARKET_ID"
⚠️ Disclaimer

OrderLens is an analytics tool.
It does not execute trades or provide financial advice.

🎯 Why This Project

Instead of exposing raw exchange data, OrderLens demonstrates how to:

Abstract market microstructure

Design clean REST APIs

Transform blockchain data into usable intelligence
