# FastAPI_Bitget_API_Bot

仅实现个人需要的功能

场景为交易员，普通场景也适用

因BG的API限制，所以用同步模式实现, sleep是防止触发API的频繁访问限制


### Install

```sh
pip install "fastapi[all]"
```

### Run 
dev

```sh
uvicorn main:app --reload
```

online

```sh
nohup uvicorn main:app --host 0.0.0.0 --port 80 &
```


### 信号 example (Tradingview)

```json
{
    "symbol": "{{exchange}}:{{ticker}}",
    "long_price": {{plot_0}},
    "stop_long": {{plot_1}},
    "short_price": {{plot_2}},
    "stop_short": {{plot_3}},
    "curr_price": {{close}},
    "action": "status"
}
```

action = {status, open, add}

Post json to https://xxx.com/tv_order_trend/


### 策略 example (Tradingview)

```json
{
    "order_action": "{{strategy.order.action}}",
    "order_contracts": "{{strategy.order.contracts}}",
    "ticker": "{{ticker}}",
    "position_size": "{{strategy.position_size}}"
}
```

Post json to https://xxx.com/tv_order_er/

