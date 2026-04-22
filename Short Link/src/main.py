from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from time import time
from .service import ShortLink
from .module import (
    EncodeRequest,
    DuplicateError,
    NotFoundError,
    FailedCreateError,
    ExcessiveFrequency,
)
from .config import Config

config = Config()
DOMAIN_NAME = config["other"]["domain_name"]
# todo
# 配置文件是可以热重载了，但是这些使用配置文件的地方还没变过来啊！要不直接上观察者模式得了😋
# 太难写了，不写了😋
# 还有数据库连接池应该和数据库操作绑定到一起，再用策略模式
app = FastAPI()
short_link = ShortLink()
short_link.init_bloom_filter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    filename="shortlink.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# note
# 这玩意全部用户共享一个限流，肯定不行
# class RateLimit:
#     """限流器，当请求超过限度时抛出 ExcessiveFrequency"""
#     period: int = config['rate_limit']['period']
#     times: int = config['rate_limit']['times']
#     record_list = []
#
#     @classmethod
#     def __call__(cls, *args, **kwargs) -> None:
#         now = time()
#         # 清理过期记录
#         cls.record_list = [t for t in cls.record_list if now - t < cls.period]
#         # 检查是否超限
#         if len(cls.record_list) >= cls.times: raise ExcessiveFrequency
#         # 记录本次请求
#         cls.record_list.append(now)


class RateLimit:
    """限流器，当请求超过限度时抛出 ExcessiveFrequency"""

    _records: dict[str, list[int]] = {}
    _period: int = config["rate_limit"]["period"]
    _times: int = config["rate_limit"]["times"]

    @classmethod
    def limit(cls, ip: str):
        now = int(time())
        if ip not in cls._records:
            cls._records[ip] = []
        # 清理过期记录
        cls._records[ip] = [t for t in cls._records[ip] if now - t < cls._period]
        # 检查是否超限
        if len(cls._records[ip]) >= cls._times:
            raise ExcessiveFrequency
        # 记录本次请求
        cls._records[ip].append(now)

    @classmethod
    def reload(cls):
        cls._period = config["rate_limit"]["period"]
        cls._times = config["rate_limit"]["times"]


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    try:
        RateLimit.limit(request.client.host)  # type: ignore
        response = await call_next(request)
        return response
    except ExcessiveFrequency:
        raise HTTPException(status_code=429)
    except Exception as e:
        raise HTTPException(status_code=404, detail=e.__str__())


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"响应: {response.status_code}")
    return response


@app.get("/favicon.ico")
def favicon():
    return FileResponse("../favicon.ico")


@app.post("/encode")
def encode(encode_request: EncodeRequest):
    """将长链接转为短链接"""
    try:
        short_code = short_link.encode(encode_request)
        return {"short_url": DOMAIN_NAME + short_code, "short_code": short_code}
    except DuplicateError:
        raise HTTPException(status_code=409)
    except NotFoundError:
        raise HTTPException(status_code=403)
    except FailedCreateError:
        raise HTTPException(status_code=500)
    except Exception as e:
        raise HTTPException(status_code=404, detail=e.__str__())


@app.get("/{short_code}")
async def redirect_to_long(short_code: str):
    """将短链接转为长链接"""
    try:
        long_url = short_link.decode(short_code)
        if not long_url:
            raise HTTPException(status_code=404, detail="短链接不存在")
        return RedirectResponse(url=long_url)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=e.__str__())


# @app.get("/{short_url}")
# async def redirect_to_long(short_url: str):
#     """访问短链接时重定向到原网址"""
#     long_url = short_link.get_long_url(short_url)  # 调用你的 service
#     if not long_url:
#         raise HTTPException(status_code=404, detail="短链接不存在")
#     return RedirectResponse(url=long_url)
