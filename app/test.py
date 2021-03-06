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


class StrategyInfo(BaseModel):
    order_action: Optional[str] = None
    order_contracts: Optional[float] = None
    ticker: Optional[str] = None
    position_size: Optional[float] = None


api_key = config['bitget_main']['api_key']
secret_key = config['bitget_main']['secret']
passphrase = config['bitget_main']['pass']
trader = config['bitget_main']['trader']

# swapAPI = swap.SwapAPI(api_key, secret_key, passphrase, use_server_time=True, first=False)
# optionAPI = option.OptionAPI(api_key, secret_key, passphrase, use_server_time=True, first=True)
# marketApi = market.MarketApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
accountApi = accounts.AccountApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
positionApi = position.PositionApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
orderApi = order.OrderApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
# planApi = plan.PlanApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
traceApi = trace.TraceApi(api_key, secret_key, passphrase, use_server_time=False, first=False)


symbol = 'BTCUSDT_UMCBL'
# new_side = 'open_long'

result = positionApi.single_position(symbol, marginCoin='USDT')
positions = result["data"]
for positionData in positions:
    # print(positionData["side"], positionData["available"])
    if float(positionData["available"]) > 0:
        result = orderApi.place_order(symbol=symbol, marginCoin='USDT', size=positionData["available"], side='close_long', orderType='market', price='', timeInForceValue='normal')

    if float(positionData["available"]) > 0:
        result = orderApi.place_order(symbol=symbol, marginCoin='USDT', size=positionData["available"], side='close_short', orderType='market', price='', timeInForceValue='normal')


# result = positionApi.all_position(productType='mix_type')
# print(result)

# result = orderApi.current('BTCUSDT_UMCBL')
# print(result)

# result = traceApi.current_track('ETHUSDT_UMCBL', 'umcbl')
# for order in result["data"]:
#     print(order)

# result = orderApi.place_order(symbol=symbol, marginCoin='USDT', size=0.01, side=new_side, orderType='market', price='', timeInForceValue='normal')
# print(result)

# result = traceApi.current_track(symbol, 'umcbl')
# order_to_close = []

# for cur_order in result["data"]:
#     if cur_order["holdSide"] == "short":
#     # new_side = "open_long"
#         order_to_close.append(cur_order["trackingNo"])
#     # order_to_close.append(cur_order["openOrderId"])
#     # elif strategyInfo.order_action == "sell" and strategyInfo.position_size < 0 and cur_order["holdSide"] == "buy":
#     # new_side = "open_short"
#     # order_to_close.append(cur_order["trackingNo"])
# # for orderNo in order_to_close:
# #     traceApi.close_track_order(symbol, orderNo)
# #     time.sleep(1)
# print(order_to_close)

if trader=='true':
    print('trader')

if trader=='false':
    print('normal')
