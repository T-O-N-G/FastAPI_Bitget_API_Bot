import json
import time
import uuid
from configparser import ConfigParser
from typing import Optional

import requests
from fastapi import FastAPI
from pydantic import BaseModel

import bitget.mix.account_api as accounts
import bitget.mix.market_api as market
import bitget.mix.order_api as order
import bitget.mix.plan_api as plan
import bitget.mix.trace_api as trace
import bitget.mix.position_api as position
import bitget.option_api as option
import bitget.swap_api as swap

config = ConfigParser()

config.read('myapi.config', encoding='UTF-8')


api_key = config['bitget_main']['api_key']
secret_key = config['bitget_main']['secret']
passphrase = config['bitget_main']['pass']

swapAPI = swap.SwapAPI(api_key, secret_key, passphrase, use_server_time=True, first=False)
optionAPI = option.OptionAPI(api_key, secret_key, passphrase, use_server_time=True, first=True)
# marketApi = market.MarketApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
# accountApi = accounts.AccountApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
# positionApi = position.PositionApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
orderApi = order.OrderApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
# planApi = plan.PlanApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
traceApi = trace.TraceApi(api_key, secret_key, passphrase, use_server_time=False, first=False)


dingUrl = "https://oapi.dingtalk.com/robot/send?access_token=8bd78539539ee4fe42e671be13287813802dddaad79d0bad0b1e268883aec156"
headers = {
    "Content-Type": "application/json",
    "Charset": "UTF-8"
}


def ding_bot(message):
    message_json = {
        "msgtype": "text",
        "text": {
            "content": message
        }
    }
    resp = requests.post(dingUrl, data=json.dumps(message_json), headers=headers)
    return resp.text


class OrderInfo(BaseModel):
    long_price: Optional[float] = None
    stop_long: Optional[float] = None
    short_price: Optional[float] = None
    stop_short: Optional[float] = None
    action: Optional[str] = None
    symbol: Optional[str] = None
    curr_price: Optional[float] = None


class StrategyInfo(BaseModel):
    order_action: Optional[str] = None
    order_contracts: Optional[float] = None
    ticker: Optional[str] = None
    position_size: Optional[float] = None


app = FastAPI()

# indicator alarm template


@app.post("/tv_order_trend/")
def tv_order_trend(orderInfo: OrderInfo):
    order_side = 1
    if orderInfo.short_price != None and orderInfo.stop_short != None:
        order_side = 2
        ding_bot("curr_price="+str(orderInfo.curr_price)+", add_short="+str(orderInfo.short_price)+", stop_short="+str(orderInfo.stop_short))
    else:
        ding_bot("curr_price="+str(orderInfo.curr_price)+", add_long="+str(orderInfo.long_price)+", stop_long="+str(orderInfo.stop_long))

    curr_positions = swapAPI.get_current_Track('cmt_btcusdt', '1', '100')  # 这里bg有bug，symbol是无效的=-=
    order_to_close = []
    order_size = 29
    averageOpenPrice = 1000000.0
    if order_side == 1:   # 当前持有空，接下来开多
        averageOpenPrice = 0.0001
    for position in curr_positions:
        if position["symbol"] == "cmt_btcusdt" and position["holdSide"] != order_side:
            order_to_close.append(position["orderNo"])
            order_size = max(int(float(position["openDealCount"])), order_size)
            if position["holdSide"] == 1 or order_side == 2:
                averageOpenPrice = max(averageOpenPrice, position["averageOpenPrice"])
            if position["holdSide"] == 2 or order_side == 1:
                averageOpenPrice = min(averageOpenPrice, position["averageOpenPrice"])

    if order_side == 1 and (averageOpenPrice-orderInfo.curr_price)/averageOpenPrice > 0.05:
        order_size = 50
    elif order_side == 2 and (orderInfo.curr_price-averageOpenPrice)/averageOpenPrice > 0.05:
        order_size = 50
    else:
        order_size += 1
    if order_size > 80:
        order_size = 80
    if order_size < 50:
        order_size = 50

    for order in order_to_close:
        result = optionAPI.close_track_order('cmt_btcusdt', order)
        print(result)
        time.sleep(1.6)

    if len(order_to_close) > 0 or len(curr_positions) == 0 or orderInfo.action == "add":
        result = optionAPI.take_order(symbol='cmt_btcusdt', client_oid=str(uuid.uuid4())[0:46], size=str(order_size), type=str(order_side),
                                      order_type='0', match_price='1', price='', presetTakeProfitPrice='', presetStopLossPrice='')
        print(result)

        time.sleep(1.7)
        result = optionAPI.take_order(symbol='cmt_btcusdt', client_oid=str(uuid.uuid4())[0:46], size=str(order_size), type=str(order_side),
                                      order_type='0', match_price='1', price='', presetTakeProfitPrice='', presetStopLossPrice='')
        print(result)
    return "ok"


# strategy alarm template
@app.post("/tv_order_er/")
def tv_order_trend(strategyInfo: StrategyInfo):
    print("ticker", strategyInfo.ticker, "order_action", strategyInfo.order_action,
          "order_contracts", strategyInfo.order_contracts, "position_size", strategyInfo.position_size)
    order_size = 0.0
    if "BTC" in strategyInfo.ticker:
        symbol = 'BTCUSDT_UMCBL'
        order_size = 0.001

    if "ETH" in strategyInfo.ticker:
        symbol = 'ETHUSDT_UMCBL'
        order_size = 0.02

    result = traceApi.current_track(symbol, 'umcbl')
    time.sleep(1)

    order_to_close = []

    new_side = ''
    if strategyInfo.order_action == "buy" and strategyInfo.position_size > 0:
        new_side = "open_long"
    if strategyInfo.order_action == "sell" and strategyInfo.position_size < 0:
        new_side = "open_short"

    # find positions need to close
    for cur_order in result["data"]:
        if strategyInfo.order_action == "buy" and strategyInfo.position_size > 0 and cur_order["holdSide"] == "short":
            order_to_close.append(cur_order["trackingNo"])
            # order_to_close.append(cur_order["openOrderId"])
        elif strategyInfo.order_action == "sell" and strategyInfo.position_size < 0 and cur_order["holdSide"] == "buy":
            new_side = "open_short"
            order_to_close.append(cur_order["trackingNo"])
        else:
            pass
            # do alarm

    # do close positions
    for orderNo in order_to_close:
        traceApi.close_track_order(symbol, orderNo)
        time.sleep(1)

    # open new position
    result = orderApi.place_order(symbol=symbol, marginCoin='USDT', size=order_size, side=new_side, orderType='market', price='', timeInForceValue='normal')
    print(result)
    return "ok"
