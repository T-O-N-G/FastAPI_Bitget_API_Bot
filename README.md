# FastAPI_Bitget_API_Bot

仅实现个人需要的功能

场景为交易员

因BG的API限制，所以用同步模式实现

修改了BG的SDK，加入开仓预设止损的字段





Install

```sh
pip install "fastapi[all]"
```

Run dev

```sh
uvicorn main:app --reload
```

Run online

```sh
uvicorn main:app --host 0.0.0.0 --port 80
```

