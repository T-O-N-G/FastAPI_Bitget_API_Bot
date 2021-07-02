import json
import time
import uuid
from configparser import ConfigParser
from typing import Optional

import requests
from fastapi import FastAPI
from pydantic import BaseModel

import bitget.option_api as option
import bitget.swap_api as swap

config = ConfigParser()

config.read('myapi.config', encoding='UTF-8')


api_key = config['bitget_main']['api_key']
secret_key = config['bitget_main']['secret']
passphrase = config['bitget_main']['pass']

swapAPI = swap.SwapAPI(api_key, secret_key, passphrase, use_server_time=True, first=False)
optionAPI = option.OptionAPI(api_key, secret_key, passphrase, use_server_time=True, first=True)


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


app = FastAPI()


@app.post("/tv_order_trend/")
def tv_order_trend(orderInfo: OrderInfo):
    order_side = 1
    if orderInfo.short_price != None and orderInfo.stop_short != None:
        order_side = 2
        ding_bot("curr_price="+str(orderInfo.curr_price)+", add_short="+str(orderInfo.short_price)+", stop_long="+str(orderInfo.stop_short))
    else:
        ding_bot("curr_price="+str(orderInfo.curr_price)+", add_long="+str(orderInfo.long_price)+", stop_long="+str(orderInfo.stop_long))

    curr_positions = swapAPI.get_current_Track('cmt_btcusdt', '1', '100')  # 这里bg有bug，symbol是无效的=-=
    order_to_close = []
    order_size = 39
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
        order_size = 40
    elif order_side == 2 and (orderInfo.curr_price-averageOpenPrice)/averageOpenPrice > 0.05:
        order_size = 40
    else:
        order_size += 1
    if order_size > 80:
        order_size = 80
    if order_size < 40:
        order_size = 40

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

#         method : POST
#         参数名	参数类型	是否必须	描述
#         :param symbol: String	是	合约名称
#         :param client_oid: String	是	自定义订单号(不超过50个字符，且不能是特殊字符，如火星字符等)
#         :param size: String	是	下单数量（不能为0，不能为负数）
#         :param type: String	是	1:开多 2:开空 3:平多 4:平空
#         :param order_type: String	是	0:普通，1：只做maker;2:全部成交或立即取消;3:立即成交并取消剩余
#         :param match_price: String	是	0:限价还是1:市价
#         :param price: String	否	委托价格（有精度限制，精度（tick_size）和步长（priceEndStep）取“合约信息接口”，限价必填）
#         :return:
# result = optionAPI.take_order(symbol='cmt_btcusdt', client_oid=str(uuid.uuid4())[0:46], size='10', type='1',
#                               order_type='0', match_price='1', price='', presetTakeProfitPrice='', presetStopLossPrice='')
# print(result)
# time.sleep(1.5)

# result = swapAPI.get_current_Track('cmt_btcusdt', '1', '100')  # 这里bg有bug，symbol是无效的=-=
# order_to_close = []
# print("-------------------------------------")
# for position in result:
#     if position["symbol"] == "cmt_btcusdt":
#         print(position["holdSide"])
#         print(position["averageOpenPrice"])
#         print(position["orderNo"])
#         print(position["openTime"])
#         order_to_close.append(position["orderNo"])
