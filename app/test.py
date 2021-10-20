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

# swapAPI = swap.SwapAPI(api_key, secret_key, passphrase, use_server_time=True, first=False)
# optionAPI = option.OptionAPI(api_key, secret_key, passphrase, use_server_time=True, first=True)
# marketApi = market.MarketApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
accountApi = accounts.AccountApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
positionApi = position.PositionApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
orderApi = order.OrderApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
# planApi = plan.PlanApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
traceApi = trace.TraceApi(api_key, secret_key, passphrase, use_server_time=False, first=False)

# result = positionApi.single_position(symbol='BTCUSDT_UMCBL', marginCoin='USDT')
# positionData = result["data"]


# result = positionApi.all_position(productType='mix_type')
# print(result)

# result = orderApi.current('BTCUSDT_UMCBL')
# print(result)

result = traceApi.current_track('ETHUSDT_UMCBL', 'umcbl')
for order in result["data"]:
    print(order)