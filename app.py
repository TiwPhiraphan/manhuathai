import re, ast, sys, string, base64, asyncio, requests, json, os, http.server, webbrowser, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image
from pathlib import Path
from pyclack.prompts import intro, outro
from pyclack.prompts.text import text
from pyclack.prompts.select import select
from pyclack.core import Option

print("\033]0;Manga Offline Reader\007", end="")

def get_base_dir() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parent

BASE_DIR = get_base_dir()
session = requests.Session()
indexs = string.digits + string.ascii_lowercase + string.ascii_uppercase
user_agent = 'Mozilla/5.0 (iPhone 17 Pro Max; CPU iPhone OS 19_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.8'
VIEWER_DIR = BASE_DIR / 'viewer'
DB_PATH = VIEWER_DIR / 'database.json'
IMG_BASE = VIEWER_DIR / 'images'
PREFIX_PATH = BASE_DIR / 'prefix.json'
MAX_TIMEOUT = (10, 240)
MAX_WORKER = 8
PORT = 80

def load_prefix() -> list[dict]:
    if PREFIX_PATH.exists():
        with open(PREFIX_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def get_selectors(url: str) -> dict | None:
    prefix_list = load_prefix()
    for config in prefix_list:
        if config['domain'] in url:
            return config['selector']
    return None

FAVICON = base64.b64decode('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o////////////319ff8AAAD/AAAA/wAAAP8AAAD/AhIW/xS64P8XzPr/Es37/xXM+f8azfr/Fsv6/xK+8/8PwPT/D8D1/xDD9f8Txfb/EMT2/w2Hp/9DREX/+/v7//////+urq7/hoaG/////////////Pz8//v7+//+/v7/5eXl////////////fX19/wAAAP8AAAD/AAAA/wECAv8PkrD/Fcz7/xXL+v8Yy/r/Fs37/xbK+f8Wzfr/D8D2/w/B9v8NvvX/D8T3/xDC9f8SwfT/E8f3/wdWaf+CgoL///////7+/v/f39/////////////u7u7/WVlZ//f39/////////////////99fX3/AAAA/wAAAP8AAAD/CmBx/xPO+/8Wyvj/Fsr5/xjM+v8bzfr/Gsz6/xXM+v8Ow/X/DMH3/wzF+P8QxPX/Dsb5/xDC9/8Pxff/EL7v/wksNf/BwcH//////////////////////+7u7v8CAgL/SEhI//Ly8v///////////319ff8AAAD/AAAA/wQuNv8Ry/T/Fc36/xnN+f8VzPr/GM36/xPN+/8azfr/Gcz5/w++8/8OxPf/DsT2/w7E+P8Ow/X/Esb4/xbG9v8SyPj/EKzR/yApLP/r6+v/////////////////7u7u/wICAv8AAAD/OTk5/+zs7P//////fH19/wAAAP8CDhD/DrTZ/xjO+v8Wy/n/Fcv5/xjL+f8Vzvv/Fs/6/xbM+v8by/n/DcD2/wzF+P8JxPr/DcT3/w7E+P8RxfX/E8X2/xHE9f8Ux/f/DYOe/1BQUP/9/f3////////////u7u7/AgIC/wAAAP8AAAD/Li4u/+Tk5P98fX3/AAEB/wyMpf8Zz/v/Gs77/xbP+v8XzPn/E837/xXM+v8WzPr/G9D7/xrN+v8Rxfb/DcH0/wrF+P8Oxvf/E8T0/xLH9/8VxfT/Fcb1/xDH+v8Ry/r/CU9e/5KSkv///////////+7u7v8CAgL/AAAA/wAAAP8BAAH/JCYn/1xbW/8KVmT/Fc77/xLN+v8Wy/r/Gc36/xXO+/8Wyfj/F8z6/xrM+f8ZzPr/HM75/wzF9/8Tw/X/EcX3/xDD9/8MyPn/EsT3/xLH9/8UyPn/E8n4/xXM+f8Vw+3/DCkw/8zMzP//////7u7u/wICAv8AAAD/AAAA/wlIVf8PnLv/BjhB/xfJ8f8Y0Pr/GNH7/xnP+v8Yzff/GMr3/xXP+v8a0fr/Gs/7/xfS/P8czvv/DMP2/xDD9v8Rxfb/C8T3/xDH+v8Vx/f/E8f3/xXJ+f8Uyfj/E8r5/xTL+v8Tp8n/KS8x//Hx8f/u7u7/AgIC/wAAAP8DHSL/GMDp/xTO+/8Yz/r/FtL7/xnR+/8Wz/v/FM37/xjL+f8b0Pn/Gsv4/xnP+/8bzPn/F836/xrN+f8Mw/f/EcT1/xHE9/8XyPX/FcX2/xTD9f8Oxvf/FcT1/xLL+v8Wyfn/FMv6/xfJ+P8KepH/X15f/+3t7f8CAgL/AgYG/xGjw/8cz/v/Fc77/xfR+/8Xz/r/Gc77/xrQ+v8Z0Pz/Gc/6/xjP+v8b0fv/G9D7/xvP+v8Zz/r/Gsz4/w/C9f8Rw/X/EsT0/xLF9v8SxfX/FMX2/xPI+P8Ux/f/E8z7/xbM+f8Wy/n/Fsz5/xPM+P8KRVH/jo6O/wMCA/8Mc4j/F837/xjP+/8Vz/v/FdD8/xnR+v8Vzvv/GdH7/xjP+v8Zzvn/GM34/xzM+P8ezvr/Gsz5/xrN+f8a0Pr/Dsf2/xDD9f8Qxfb/E8Py/xbF9f8Vx/b/E8n4/xbJ+P8UzPr/Fc77/xfL+v8Zy/n/Fc36/xTC6f8LIyj/CT9J/xjN+f8U0fv/Fc/6/xbP+/8T0/v/FdD6/xbS+/8W0Pv/GtD6/x3O+f8Z0Pn/HND6/x3O+f8fzfn/IND6/xrQ+/8Qwvb/Esf3/xXD8/8TxPT/FMX1/xHG9/8Sx/f/FMn3/xTL+P8Xy/n/F8r2/xbK+f8Wy/r/F876/xGlxv8WvuX/GM/8/xfO+/8ZzPv/GM/7/xbQ+/8Xz/n/F9D7/xrR+v8az/v/HM/6/x7P+f8azvr/G9D6/x3R+v8a0fv/IND6/w3F9v8TwvT/EMj4/xDD9v8TxvX/FMn4/xTK+f8Xyvj/GMv4/xnK9/8Xy/n/Gs35/x7P+/8Yzvv/HND7/xrP+/8az/z/Gs77/xrS+/8Z0vz/FtH8/xbQ+/8b0Pr/GNH7/xrR+/8Zz/r/Gc76/x7P+v8fz/n/Is34/x/O+f8bz/n/EcLz/xDE9f8Qx/b/EMP0/xPF9f8Tx/b/FMf4/xPK+P8WyPb/Fcr5/xjK+f8ZzPr/Gsn3/xvN+f8Yzvv/GdH6/xrR+v8bzPv/HM/6/x3R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+/8Ly/v/Ccn8/wrK+/8Lyfv/DMj7/xHL+v8Oy/v/Dcv7/wrM+/8Oyvn/Csn8/xHN+/8My/z/B8v8/wjL+v8Iyvr/Bsr7/wvL+/8Oy/v/Dsj6/xG88v8PvPP/Ebrz/xK58P8Tu/L/FLvw/xK78f8PvvX/D7/1/xLC9v8SvvX/DsL3/xK/8/8OxPj/EMX3/xG+9P8RxPf/DMP5/xDD+P8Qxvn/Ecb5/wjJ/P8LyPv/C8j7/wnH/P8JyPv/Csf7/wzK/P8Jyvv/D8n6/wzK+/8Lyfv/Dcv6/xDI+v8Qyvv/Esv6/w3K+/8Qyfr/Dcn7/xDK+/8LyPv/Csz7/wrI+v8My/r/DMr7/wzL+/8Myvv/Dsn6/xK68f8SuvP/Dbz2/w++9P8SuvH/EsDz/w689f8Nv/f/EcD1/xW89f8UvvH/EcX2/xPD9/8Uwvf/EcT2/xLF+P8Ox/r/DcH4/xDI+f8SxPb/Esf5/wzG+v8Kyfv/Dcf7/w7I/P8Kyvz/Dcf8/wvJ/P8Hyfz/Ccj7/w7L+/8Oyfr/EMn5/xHL+v8NzPz/EMf6/xDL+v8Sxvn/Dcf5/w/H+f8Myfv/Ccv6/xTL/P8Lyfv/Ccj8/wzJ/P8Pyfr/Esn5/w698/8OvPX/Er70/w+99P8PwPf/D7rw/xO+8/8Wwfb/DMD3/xLA9f8Qwfb/Ebz0/w+98/8MxPj/EsX3/w7F+P8Oxvn/EMn5/xDH+f8Ox/r/Dsj6/xDH+v8Pyvv/DMr8/w/H+v8Lx/v/C8j8/wrJ/P8Kyvz/Dcv7/wzJ/P8Oyvz/Dsj6/wzK+/8Oyvr/E8X3/w/I+f8Qzfv/C8z7/wzM/P8Oyfv/Dsn7/w7K/P8Oyfv/Dsr7/xDK+f8Ryvv/EM77/w299f8RuvL/D731/xC89f8UvPL/Fbrv/xS98f8SvPP/DL/3/xLB9v8Rwvf/DcT4/xTB8/8OxPb/EsT1/xDE+P8Tx/n/Ecn6/xLI+f8Mxvr/DMb6/w7K+v8OyPr/DMj6/w/K+/8LyPv/Dsr7/wvK+/8Kyvz/Csv8/xDL+/8Sy/v/Ecr7/xDL+/8Qy/v/FMz5/xLM+/8Qy/v/Dsz7/xDI+v8Tyvn/Fcv5/w7L+/8Qyvv/Dcv7/xLL+/8SzPv/D8z7/xLA8v8QvvT/DsL2/xC/9v8UwPX/FMDz/xG+9f8Qv/b/Fb3z/xPC9f8Uw/f/DsH0/xHB9v8Rxfj/D8f5/xLI+v8Pw/b/FsP3/xDE+f8Oyfv/D8n7/wzH/P8KyPv/DsX6/w7F+v8Ox/v/Dsb6/wzJ/P8Iyvz/Dsz8/xHM/P8Oy/v/EMr6/w/J+/8Szfv/Es78/w/N/P8Qy/v/D837/xLM+/8Szfv/Ecr7/wzI+v8Tyfv/Es38/xLO/P8Py/v/D8j6/xK99/8Pv/X/E7zz/xC58f8TuO//Dr/0/xO/8v8RvvP/EcL2/xfA8v8WwvT/FMT1/xPE9f8UwvX/EsH3/xDC9/8RxPj/DMT4/w3G+/8Oyfv/EMn7/w7J/P8Oyvv/Dsn8/w7K+/8Px/v/Dsn6/wzK/P8Ly/v/DMv8/w/K/P8Lyvv/C877/xPQ+/8Syfn/D8X4/xHJ+v8Sy/v/Esf5/xPL+f8Qy/j/FMv7/xXO+/8Oy/v/Ds38/w7L+/8Oyvv/Esr5/xC99P8RvfT/E73y/wy/9f8RvvP/D8L1/xW+8v8Sv/P/Er/1/xPA9/8QvvX/E8Hz/xDG9/8SwfX/E8X2/xPI+f8QyPn/Ecv7/wzJ/P8Myvv/Dcf6/xHK+v8Nx/v/EMj6/w3K/P8Oyfv/Fcf4/w/L+/8Ny/v/C8v7/wzJ+/8Ny/v/Dsv7/xDJ+v8Szfr/EM37/xPJ+v8Uy/r/EMz7/xTM+v8TzPr/Dsv7/w7K/P8Pyfv/D8f6/xDL+v8Oy/v/Ecv7/xC47f8PvPT/C8D3/w299f8TvvL/Er/0/xK/8/8Twvb/EMP2/xDC9v8SwvX/EsHz/xLD9f8Uxff/Esj6/xDB9/8Pxfn/Dcf6/xDH+v8OyPv/Dsr7/xHK+/8Pyvv/EMn6/wzL+/8Oyfv/Esv7/w/K+/8Pyfn/DMf6/xPM+v8PyPr/D8v7/xLM+v8Nyvr/E836/xTN+v8Ry/r/Dcv7/xLL+/8Wzvr/EMz7/w3H+/8MyPv/Ecz7/xPK+/8Oyvv/Ecz5/xu+8v8VvvP/D8P5/xG/9v8Qwvb/FsH0/xTD9P8Qwvb/D8L0/w/B9f8RxPb/FcD0/xPB9f8SyPn/EMb5/xDG+f8Nxvr/Csj7/w/I+v8Ryvv/EMj6/xLI+f8PyPr/C8j7/xHK+/8Myvz/Dsz8/xHO+/8Rzfv/E878/w/K+/8NzPv/E8/7/xPO+/8My/v/Ecf6/xHK+v8MzPv/D878/wzK+/8MyPr/Dsr7/wrP+/8Pzvz/E8n6/xTL+v8Uzvv/E836/xC/9P8OwPX/EMD1/xK+8v8PwvT/D8T4/xCq0/8MhKb/D4Ol/wiHp/8NhKX/Doam/xCHpv8Mh6f/Coep/wmIqP8Hian/C4ep/xGLp/8Kian/DIap/wiKqv8Hi6r/CYqo/weIqf8KiKn/DImp/wuJqf8Kiqn/DYuq/wqMqf8Hian/Coup/wuGqf8Jiqn/DYyo/wyMqP8Jiqn/CImp/wqJqf8Ki6r/DbXb/w3K+f8QzPz/Esv6/xbL+f8Ryfn/Dsv6/w+98/8QwfX/EcD0/xTD9f8Mwvf/D8D2/wygz/8FKDL/CRIV/x8qLP8fKSz/Hiks/x0oK/8MFxr/AQwP/wEMD/8CDhD/GiUn/yArLP8eKSz/Hyks/x4qLP8eKSv/BxIV/wAMD/8FERP/Gycp/x4pLP8eKiz/Hios/xklJ/8BDRD/AQ0P/wEMD/8BDQ//Ag0P/wEND/8BDQ//AQwP/wEMD/8EMTj/Cbba/xPK+f8Ryfr/F8r6/xfK+/8Uyfn/EMj7/xPC9f8Owvj/DsD2/w289P8PxPf/Er7y/xa/7/8NdZD/CRET/7S0tP/4+Pj/+vr6//j4+P+Wlpb/DAwM/wAAAP8JCQn/zc3N//v7+//6+vr/+vr6//r6+v/6+vr/kpKS/wcHB/8kJCT/3Nzc//r6+v/6+vr/+vr6/8bGxv8GBgb/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wELDv8Lf5v/D8n6/xDM+/8Vzvr/FM38/xfL+v8VzPv/FMz7/wy+9f8Qv/T/D8L0/w/A9f8PwPT/Eb/x/xPB9P8SuOX/CEte/ywsLf/Pz8/////////////w8PD/Y2Nj/wEBAf8JCQn/z8/P////////////////////////////+Pj4/2pqav8nJyf/39/f/////////////////8jIyP8FBgb/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAEB/whXaP8Uxe//Fc37/w7M+/8Pzfv/Esz6/xjM+v8Wzvr/Gc36/xLB8f8PwfX/DsP0/xHE9f8Sw/X/DsT1/xHF9/8TwvX/Drfk/wctNv9cXFz/7+/v////////////6urq/zY2Nv8JCQn/z8/P/////////////////////////////////+Li4v9lZWX/39/f/////////////////8jIyP8GBgb/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/BDA7/xbE6v8Xzfv/Fs36/xTN/P8Yzfn/Fc35/xjO+/8azPr/FMz6/w/B9P8SvvP/DL70/w6+9P8Ov/X/Fcb0/xLE9f8Tx/X/DsX4/w+gxP8KHSL/l5eX//z8/P///////////8vLy/8nKCj/z8/P///////////////////////8/Pz//v7+//7+/v/U1NT/7+/v/////////////////8jIyP8GBgb/AAAA/wAAAP8AAAD/AAAA/wAAAP8EGyD/EajL/xLL+v8Wyvv/F836/xfL+f8Wy/r/GM/7/xfJ+f8Yyvn/E837/w/A9f8SwfX/EcP1/w7B+P8Pw/X/DMP3/xHE9/8TvvL/D8P3/xO/7/8LcIn/FRwf/7i4uP/+/v7///////j4+P+XmJj/2tra//////////////////v7+//BwcH/5OTk///////+/v7//v7+/////////////////8jIyP8GBgb/AAAA/wAAAP8AAAD/AAAA/wILDP8NeZL/EMn2/xXN+v8Ty/r/FMf4/xnL+v8YzPv/Fs37/xnJ+P8XzPr/Fc36/w++9f8PvvX/DcH3/w+88/8QwPX/DMP4/w7B9P8TxfX/EMH1/xDF9/8QvOn/B0NQ/y8vL//Y2Nj////////////z8/P/+fn5//////////////////n5+f92dnb/RkZG/+np6f///////////////////////////8jIyP8GBgb/AAAA/wAAAP8AAAD/AQAB/wlNWf8Txu//E9D7/xnM+f8Yy/n/F8r4/xfO+/8azfr/Hsz5/xnP+v8Yy/v/FM/7/wrE+P8Qvvb/C8P5/w3H+P8PwvX/E8b0/xLG+P8Ow/j/EcL3/xDG9/8Ow/j/DrTg/wciKf9nZ2f/8vLy//////////////////////////////////n5+f9xcXH/AQEB/zo6Ov/X19f//f39/////////////////8jIyP8GBgb/AAAA/wAAAP8AAAH/BCcu/w7A6P8V0Pv/Fcv5/xnN+f8Xyfj/E837/xbQ+/8Z0Pv/FM37/xfM+v8byvj/Gs36/xHA8v8QwfT/Csb3/w3D9v8Nwvf/DcX4/w7D9v8NxPf/FcX4/xTD9P8TyPn/Fcf4/w6Ttf8SJir/m5ub//7+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+/8b0fr/GdD6/xjP+/8Xz/v/Gs76/xrM+f8Zzvr/HNH7/x7N+f8bz/v/HND6/xvO+f8Zy/j/GND6/w/A8P8RwfT/E8Pz/xXD8v8Tx/b/FcX2/xPD9P8TyPb/FcT2/xbH9/8Tx/j/FMP0/xXL+/8TzPr/F876/xLH+f8Vzfr/Fcr3/xvN+v8Tut//Bi41/0BAQP9eX1//AgEB/wxoeP8WyfX/Fs/8/xnR/P8X0vz/F837/xrR/P8Y0vv/HNT7/xrP+v8U0Pv/HNL8/xnP+v8a0fr/GM75/xjM+P8Zzvn/G8z4/xzP+/8Zy/n/Hsz5/xnK+f8Z0Pr/GdD6/w7M+P8Sw/X/Ecn3/xDE9P8QxvX/FL/w/xjE8/8SxvX/FMb3/xTK+f8Tyfj/G8r4/xTL+f8Ty/r/FM/7/xrO+v8azvr/HM35/xbK+f8Vzfv/F6jJ/wgXGv8PEBD/CT1G/xjJ9P8Vzvz/FtP7/xfR+/8Ry/r/F877/xPS/P8S0fv/EtH7/xnT+v8W1Pz/FdH8/x/T+f8bz/r/H875/xnS+/8azfj/GtD6/xvP+v8fz/j/Hsn3/yDQ+v8f0fv/GtD6/wzF9/8QxPX/EMb2/xPH9/8UxfP/E8Lz/xPH9v8Vyvj/Fcf2/xXK9/8WyPb/Fsj4/xbN+f8Vzfv/Fcz6/xbL+f8Yy/n/Fcn5/xbP+/8Tzvv/FtH6/w2CnP8INj7/Fa7R/xfR/P8Z0Pv/Es/6/xjN+v8X0Pv/FtH7/xfS+/8X0fr/FtD6/xbQ+/8W0Pr/F8z6/xjM+f8Yz/v/Gcz4/xrP+f8czfj/HtD6/xzO+v8h0vr/Hs76/xzR+/8cz/v/G9D7/xPA9f8Rw/f/EML2/xLD8/8WxvX/E8Ly/xXE9P8UwfP/EMf4/w/G+f8RyPf/EMb3/xbI9/8Tzfv/Gsr4/xnD8f8TzPr/Fcr5/xjO+v8Vyvn/F837/xPJ8/8XuN3/F875/xrP/P8Xzfv/GdD7/xfM+v8ezfv/FtD8/xTQ+/8W0Pv/Gs/3/xvS+/8Y0vv/GdP7/x3Q+/8b0fv/H9H6/yDQ+/8c0vr/F9D6/xrQ+v8Zz/n/HtP7/xvR+/8k0vn/GtH7/w/I9/8PxPb/E8H0/xPJ9/8PxPf/Esb1/xTE9P8UyPf/FMf5/xXJ+P8Uyff/HM75/xfL+P8Yzfn/G8j1/xnM+P8czvr/Gsz4/xvQ+/8cz/v/Fs78/xzQ/P8c0Pv/G9D8/xzR/P8az/z/GM/8/xnU/P8X0fz/GdP7/xjQ/P8Z0/z/FtD6/xzR/P8b0fr/GdH6/xnS/P8YzPr/GM/6/xrN+/8Zz/v/IdH6/yHO+P8i0fr/IMz5/yLN+v8czPn/F8/5/w/E9f8Ow/T/FcXz/w7F9v8Pxvb/D8T2/xPK9/8Txvb/FMf2/xfJ+f8Tyvn/E8n5/xfE9f8YzPj/Fsn5/xbK+P8XzPr/Gs36/x7O+v8ay/r/Gc77/xnO+/8a0fv/Gc/7/xrP+/8Zz/v/G837/xzQ+v8d0Pv/HND7/xfQ/P8Wz/v/FtH7/xnS+/8X0Pr/HdP7/xzR+/8a0fv/HdH6/xrP+v8azvr/H834/yDQ+v8gzvn/I874/yHP+P8Zzvn/INP7/xK/8f8Pxfb/DsH0/xPK9/8QxfX/DcH1/xbK9/8PxPT/Fsf2/xPE9f8SyPn/FMv5/xnL9/8TyPj/Fcz6/xfK+f8Yy/v/GMr6/xnI9f8ey/j/GM/7/xnP+/8W0Pv/HND5/xrP+P8czvz/G837/x7S+v8Z0fr/HM/6/x3T/P8b0fz/G9P7/xrP+P8b0/v/HtP8/x7M+P8e0/z/HNH7/xzR+v8ezvj/IdD5/x/L+P8i0fr/I9H6/yHO+P8kzvf/Ic77/xDH8/8Rxfb/Dsb1/xTD9P8QxfX/FMv3/xDJ+f8Sy/j/FMn2/xLI9v8Uyff/Esz6/xLL+v8Vyvf/Fcz4/xbL+f8azPn/Gs35/x/N+P8cyvn/HdD6/xnR/P8dz/v/H836/xvQ+/8Uz/v/G9T8/x7N+v8bz/v/GtT8/xrT/P8c0/r/GtP7/x7S+v8cz/v/Fs77/yDT+f8g0fv/GdH7/xnR/P8g0/v/JdH6/x/R+/8hz/r/H9D5/x7P+v8jz/j/HM35/w/H9v8SxPX/FMPx/xfG9f8Vx/X/F8f1/xPE9v8Txfb/E8j4/xXK9/8VyPf/GMv3/xfO+v8Yyff/Fcv6/xnM+f8czPn/Gcv3/x3H9/8Zy/n/IND7/x3R+/8c0Pr/GM37/xrP+/8d0vv/G9H7/x/W+/8d0/v/G9H8/xvT+/8b1Pr/H9L5/x3T+/8b0/v/HNL7/x3T+/8f0fv/GtL8/yPT+/8g0fr/IdH7/xzP+v8dz/n/Ic34/yDP+f8gz/j/HdL5/xDC9P8Rxvb/D8Lz/xXH9/8TxfX/F8n4/xPF8/8TxvT/E8Tz/xjL9f8Wy/r/GLvs/xnM+P8YzPn/Hc34/x/K9f8byvj/HMz5/xrI9/8c0fv/Hs/7/x3N+/8d0vv/JND7/x7T/P8czvz/IdL6/x7T+/8f1fz/HdP8/xvV/P8e0/r/H9H4/x7V+/8c0fr/Gs33/x7S+f8h0fv/HtT8/xjS/P8X0Pv/INX8/yHR+/8bz/r/HdP7/yDP+v8g0fr/H9b7/xPD9P8Qv/T/FsHx/xG98f8OxPX/Db/z/xLF9f8Txvb/Gsj4/xrE8/8Wyvj/Fcr3/xrK9/8ay/j/Gs74/xzM9/8V0fv/F876/xjP+/8bzfr/Gs/7/xrR+/8b0fv/Gs/7/yLT/P8a0vz/INH8/x7T+/8ezfr/HdT7/xjR/P8d0/v/H9T7/yDV+/8i1fv/JdL3/yDQ9v8d0fr/HNL7/xfP+/8d0Pv/H9D7/yPM9v8l0fn/I9b7/yPQ+v8k0fr/HtH7/xDF9v8Tx/b/Fb3v/xjI9f8Ux/b/FMr4/xjJ9f8Yyff/GMr4/xjD8v8Yy/n/Gcr3/xbO+v8Yzfj/GMv3/xjO+v8Wy/j/F8/6/x3P+v8f0vr/HND6/yLV+/8h0vv/IdH7/x/Q+v8az/v/G9P7/xrQ+v8c0Pr/HdD7/xrR+/8e0Pr/HdL7/xnS/P8c0fv/HdP7/xzU+/8gzvr/Hs/6/yHT+f8e1Pv/INL7/yPQ+f8j0Pn/IdH5/yLQ+v8h0Pr/H9P7/xXB8f8SwvP/EsT2/xHF9v8Rw/P/Esj2/xjE8v8Wx/b/Fcj4/xfD8/8Ux/b/GMv3/xLK+f8ZzPn/HtH5/xrP+/8Xz/r/F8n5/xvO+v8dzfn/H9T6/yDP+v8bzvr/HdH7/yHT+/8Y1fz/GtH8/xvT+/8h1vv/ItP7/yHY+/8g0vr/GtH6/xzU+/8h0/v/INX6/x7R+/8b0Pv/HtD6/xfT/P8ZzPn/HtL5/yPU+v8l0/n/IM33/yDR+/8h0Pr/HtD7/xLF9P8Sxvb/E8b1/xHB8v8Ux/f/F8v2/xHF9v8UxPP/FMb3/xfB8f8azPj/FM76/xnO+v8bzvj/HM76/xrM+f8Xy/n/HdH5/yHQ+P8f0fv/Gc36/xrR/P8Zzfv/GtH8/x7U+v8f1vz/GdH7/xnU+/8d1Pn/I9b6/yDV+P8f1Pv/INT7/x3R+v8e0/v/Idf8/yDU+v8f0Pn/HM34/xjQ+/8gz/n/H8/5/yHP+P8f0vr/IdT4/yTR+f8i0vr/HdT7/xLF9f8Txfb/EMT3/xLC8/8Rx/X/Esn3/xPF9v8VxvT/Fsf1/xnK9v8cy/f/Gs34/xnK+P8Wyvn/G8r4/xjK+P8byPf/GMv5/xvQ+v8Zz/v/G8z5/xbM+f8bzPn/H9H7/xvP+v8Z0vr/HtX7/x3W+/8d0Pj/HdT6/xzP+f8Zzvv/G8/6/x/R+v8f0Pn/G9L6/x3T+/8e0Pr/HNH7/x/R+f8k0fj/JtH5/yDT+f8b0/r/GtL5/x/M9/8e0/n/H9X7/xHG9/8Pxfb/EcP1/xDK+P8QyPf/Fsz4/xfI9/8azPb/F8T0/xnO+f8Xy/f/GM34/yDL9/8hyfX/Fcf3/xjJ+P8Vxvb/Gc/6/xrQ+f8czPf/G8v7/x/Q+/8g0vr/HtH6/xrR+/8c0Pv/HNH6/xrS+/8h1fv/IdP7/ybX+/8i1vv/IdT7/yHO+v8i1vr/INT6/xzR+/8h0Pr/IdL7/yDO+f8jz/j/Jc75/yHU+v8e0vn/IdL4/yTT+v8Z0/v/GtT6/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==')
INDEX_HTML = '''<!Doctype html><html lang=en><meta charset=UTF-8><meta content="width=device-width,initial-scale=1" name=viewport><title>Manga Reader</title><style>.ep-item:hover,.manga-item-title,body{color:var(--text)}#main,body{min-height:100vh}#topbar,.sidebar-header{border-bottom:1px solid var(--border)}.ep-item,.nav-btns{gap:8px;display:flex}.nav-btn,body{font-family:'Noto Sans Thai',sans-serif}#loading,body::before{position:fixed;inset:0}#error-state.show,#loading.show,#main,#reader,#sidebar,#topbar,#welcome,.ep-item,.nav-btns{display:flex}:root{--bg:#0a0a0f;--surface:#12121a;--border:#1e1e2e;--accent:#e8c97a;--accent2:#c45c7a;--text:#e8e8f0;--muted:#6b6b8a;--panel:#0f0f18}*{margin:0;padding:0;box-sizing:border-box}body{background:var(--bg);overflow-x:hidden}body::before{content:'';background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");pointer-events:none;z-index:9999;opacity:.4}#sidebar{position:fixed;left:0;top:0;bottom:0;width:280px;background:var(--panel);border-right:1px solid var(--border);flex-direction:column;z-index:100;transform:translateX(0);transition:transform .3s cubic-bezier(.4,0,.2,1)}#sidebar.collapsed{transform:translateX(-280px)}.sidebar-header{padding:28px 24px 20px}.sidebar-header h1{font-family:'Bebas Neue',sans-serif;font-size:26px;letter-spacing:3px;color:var(--accent);line-height:1}.sidebar-header p{font-size:11px;color:var(--muted);margin-top:4px;letter-spacing:1px;text-transform:uppercase}#manga-list{overflow-y:auto;flex:1;padding:12px 0}#manga-list::-webkit-scrollbar{width:4px}#manga-list::-webkit-scrollbar-track{background:0 0}#manga-list::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}.manga-item{padding:14px 24px;cursor:pointer;border-left:3px solid #fff0;transition:.2s}.manga-item:hover{background:rgb(232 201 122 / .05)}.manga-item.active{border-left-color:var(--accent);background:rgb(232 201 122 / .08)}.manga-item-title{font-size:13px;font-weight:600;margin-bottom:3px}.manga-item-count{font-size:11px;color:var(--muted)}.ep-section{border-top:1px solid var(--border);padding:12px 0}.ep-section-title{font-size:10px;letter-spacing:2px;color:var(--muted);text-transform:uppercase;padding:0 24px 8px}.ep-item{padding:8px 24px;cursor:pointer;font-size:12px;color:var(--muted);transition:.15s;align-items:center}.ep-item::before{content:'';width:4px;height:4px;border-radius:50%;background:var(--border);transition:background .15s;flex-shrink:0}#breadcrumb span,.ep-item.active{color:var(--accent)}.ep-item.active::before,.ep-item:hover::before{background:var(--accent)}.ep-item.active{font-weight:600}#main{margin-left:280px;transition:margin-left .3s cubic-bezier(.4,0,.2,1);flex-direction:column}#toggle-sidebar,.nav-btn{cursor:pointer;transition:.2s}#main.expanded{margin-left:0}#topbar{position:sticky;top:0;z-index:90;background:rgb(10 10 15 / .9);backdrop-filter:blur(12px);padding:12px 24px;align-items:center;gap:16px;transition:transform .3s ease,opacity .3s ease}#topbar.hidden{transform:translateY(-100%);opacity:0;pointer-events:none}#toggle-sidebar{background:0 0;border:1px solid var(--border);color:var(--muted);padding:6px 10px;border-radius:6px;font-size:16px;line-height:1}#breadcrumb,.nav-btn{color:var(--muted);font-size:12px}#toggle-sidebar:hover,.nav-btn:hover:not(:disabled){border-color:var(--accent);color:var(--accent)}#breadcrumb{flex:1;letter-spacing:.5px}.nav-btn{background:var(--surface);border:1px solid var(--border);padding:6px 14px;border-radius:6px}#error-state h2,.welcome-title{font-family:'Bebas Neue',sans-serif}.nav-btn:disabled{opacity:.3;cursor:not-allowed}#reader{flex:1;gap:0;flex-direction:column;align-items:center;padding:32px 16px 80px;cursor:pointer}#reader img{max-width:min(800px, 100%);width:100%;display:block;pointer-events:none}#reader img:first-child{border-radius:4px 4px 0 0}#reader img:last-child{border-radius:0 0 4px 4px}#welcome{flex:1;flex-direction:column;align-items:center;justify-content:center;gap:16px;padding:60px 24px;text-align:center;cursor:pointer}.welcome-icon{font-size:64px;filter:grayscale(.3);animation:3s ease-in-out infinite float}@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}.welcome-title{font-size:32px;letter-spacing:4px;color:var(--accent)}#loading p,.welcome-sub{font-size:13px;color:var(--muted)}.welcome-sub{max-width:320px;line-height:1.7}#progress-bar{position:fixed;bottom:0;left:280px;right:0;height:3px;background:var(--border);z-index:200;transition:left .3s}#progress-bar.expanded{left:0}#progress-fill{height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2));transition:width .2s;width:0%}#loading{display:none;background:rgb(10 10 15 / .8);backdrop-filter:blur(4px);z-index:500;align-items:center;justify-content:center;flex-direction:column;gap:16px}.loader{width:40px;height:40px;border:2px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:.8s linear infinite spin}@keyframes spin{to{transform:rotate(360deg)}}#error-state{display:none;flex:1;align-items:center;justify-content:center;flex-direction:column;gap:12px;text-align:center;padding:40px}#error-state .err-icon{font-size:48px}#error-state h2{color:var(--accent2);font-size:24px;letter-spacing:2px}#error-state p{color:var(--muted);font-size:13px;max-width:300px;line-height:1.6}@media (max-width:700px){#sidebar{width:260px;transform:translateX(-260px)}#sidebar.open{transform:translateX(0)}#main{margin-left:0}#progress-bar{left:0}.sidebar-overlay{display:none;position:fixed;inset:0;background:rgb(0 0 0 / .5);z-index:99}.sidebar-overlay.show{display:block}}</style><div id=sidebar><div class=sidebar-header><h1>MANGA</h1><p>Offline Reader</p><a href=library.html onmouseout='this.style.color="var(--muted)"' onmouseover='this.style.color="var(--accent)"' style="display:inline-block;margin-top:10px;font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);text-decoration:none;font-family:monospace;transition:color .2s">← Library</a></div><div id=manga-list></div></div><div id=overlay class=sidebar-overlay onclick=closeSidebar()></div><div id=main><div id=topbar><button id=toggle-sidebar onclick=toggleSidebar()>☰</button><div id=breadcrumb>Select a manga from the sidebar</div><div class=nav-btns><button id=btn-prev onclick=changeEpisode(-1) class=nav-btn disabled>◀ Prev</button><button id=btn-next onclick=changeEpisode(1) class=nav-btn disabled>Next ▶</button></div></div><div id=welcome><div class=welcome-title>MANGA READER</div><div class=welcome-sub>Select a manga from the sidebar, then choose an episode.</div></div><div id=reader style=display:none></div><div id=error-state><h2>LOAD FAILED</h2><p>No images found for this episode. Try downloading again. </div></div><div id=progress-bar><div id=progress-fill></div></div><div id=loading><div class=loader></div><p>Loading...</div><script>let db={},currentKey=null,currentEpIndex=null,isMobile=window.innerWidth<=700;function toggleTopbar(){document.getElementById("topbar").classList.toggle("hidden")}function getParams(){const e=new URLSearchParams(window.location.search),t=e.get("episode");return{manga:e.get("manga"),episode:null!==t?parseInt(t)-1:null}}function pushState(e,t){const n=new URLSearchParams;null!==e&&n.set("manga",e),null!==t&&n.set("episode",t+1);var o=`${window.location.pathname}?${n.toString()}`;window.history.pushState({manga:e,episode:t},"",o)}async function init(){try{const o=await fetch("database.json");if(!o.ok)throw new Error("no db");db=await o.json(),renderMangaList();var e,{manga:t,episode:n}=getParams();t&&db[t]&&((e=document.querySelector(`.manga-item[data-key="${t}"]`))&&(selectManga(t,e,!0),null!==n&&db[t].episodes[n]&&loadEpisode(t,n,!0)))}catch(e){document.getElementById("welcome").innerHTML='<div class="welcome-title">NO DATA</div><div class="welcome-sub">database.json not found.<br>Run <code style="color:var(--accent)">python downloader.py</code> and choose Download first.</div>'}}function renderMangaList(){const e=document.getElementById("manga-list");e.innerHTML="";for(const[o,t]of Object.entries(db)){const n=document.createElement("div");n.className="manga-item",n.dataset.key=o,n.innerHTML=`<div class="manga-item-title">${t.title}</div><div class="manga-item-count">${t.episodes.length} episodes</div>`,n.onclick=()=>selectManga(o,n),e.appendChild(n);const s=document.createElement("div");s.className="ep-section",s.id=`eps-${o}`,s.style.display="none",s.innerHTML='<div class="ep-section-title">Episodes</div>',t.episodes.forEach((e,t)=>{const n=document.createElement("div");n.className="ep-item",n.dataset.index=t,n.textContent=`Episode ${e.ep}`,n.onclick=e=>{e.stopPropagation(),loadEpisode(o,t)},s.appendChild(n)}),e.appendChild(s)}}function selectManga(e,t,n=!1){document.querySelectorAll(".manga-item").forEach(e=>e.classList.remove("active")),document.querySelectorAll(".ep-section").forEach(e=>e.style.display="none"),t.classList.add("active"),document.getElementById(`eps-${e}`).style.display="block",currentKey=e,n||pushState(e,null)}function loadEpisode(e,t,n=!1){currentKey=e,currentEpIndex=t;const s=db[e].episodes[t];if(s){n||pushState(e,t),document.getElementById("topbar").classList.remove("hidden"),document.getElementById("loading").classList.add("show"),document.getElementById("welcome").style.display="none",document.getElementById("reader").style.display="none",document.getElementById("error-state").classList.remove("show"),document.querySelectorAll(".ep-item").forEach(e=>e.classList.remove("active"));const d=document.querySelector(`#eps-${e} .ep-item[data-index="${t}"]`);if(d&&(d.classList.add("active"),d.scrollIntoView({block:"nearest"})),document.getElementById("breadcrumb").innerHTML=`${db[e].title} <span>/ Episode ${s.ep}</span>`,document.getElementById("btn-prev").disabled=t<=0,document.getElementById("btn-next").disabled=t>=db[e].episodes.length-1,!s.images||0===s.images.length)return document.getElementById("loading").classList.remove("show"),void document.getElementById("error-state").classList.add("show");const a=document.getElementById("reader");a.innerHTML="";let o=0;const i=s.images.length;s.images.forEach((e,t)=>{const n=document.createElement("img");n.src=e,n.alt=`Page ${t + 1}`,n.onload=n.onerror=()=>{o++,o>=Math.min(3,i)&&(document.getElementById("loading").classList.remove("show"),a.removeAttribute("style"),window.scrollTo(0,0))},a.appendChild(n)}),isMobile&&closeSidebar(),window.scrollTo(0,0),updateProgress()}}function changeEpisode(e){null!==currentKey&&null!==currentEpIndex&&((e=currentEpIndex+e)<0||e>=db[currentKey].episodes.length||loadEpisode(currentKey,e))}function updateProgress(){var e=window.scrollY,t=document.body.scrollHeight-window.innerHeight,t=0<t?e/t*100:0;document.getElementById("progress-fill").style.width=t+"%"}function toggleSidebar(){if(isMobile)document.getElementById("sidebar").classList.toggle("open"),document.getElementById("overlay").classList.toggle("show");else{const e=document.getElementById("sidebar"),t=document.getElementById("main"),n=document.getElementById("progress-bar");e.classList.toggle("collapsed"),t.classList.toggle("expanded"),n.classList.toggle("expanded")}}function closeSidebar(){document.getElementById("sidebar").classList.remove("open"),document.getElementById("overlay").classList.remove("show")}document.getElementById("reader").addEventListener("click",toggleTopbar),document.getElementById("welcome").addEventListener("click",toggleTopbar),window.addEventListener("scroll",updateProgress),window.addEventListener("popstate",e=>{var{manga:t,episode:e}=e.state??getParams();if(t&&db[t]){const n=document.querySelector(`.manga-item[data-key="${t}"]`);n&&selectManga(t,n,!0),null!=e&&db[t].episodes[e]&&loadEpisode(t,e,!0)}}),document.addEventListener("keydown",e=>{"ArrowLeft"!==e.key&&"ArrowUp"!==e.key||changeEpisode(-1),"ArrowRight"!==e.key&&"ArrowDown"!==e.key||changeEpisode(1)}),window.addEventListener("resize",()=>{isMobile=window.innerWidth<=700}),init()</script>'''
LIBRARY_HTML = '''<!Doctype html><html lang=en><meta charset=UTF-8><meta content="width=device-width,initial-scale=1"name=viewport><title>Library</title><style>@font-face{font-family:Bebas Neue;font-style:normal;font-weight:400;src:url(/cf-fonts/s/bebas-neue/5.0.18/latin/400/normal.woff2);unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD;font-display:swap}@font-face{font-family:Bebas Neue;font-style:normal;font-weight:400;src:url(/cf-fonts/s/bebas-neue/5.0.18/latin-ext/400/normal.woff2);unicode-range:U+0100-02AF,U+0304,U+0308,U+0329,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20CF,U+2113,U+2C60-2C7F,U+A720-A7FF;font-display:swap}@font-face{font-family:DM Mono;font-style:normal;font-weight:300;src:url(/cf-fonts/s/dm-mono/5.0.18/latin/300/normal.woff2);unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD;font-display:swap}@font-face{font-family:DM Mono;font-style:normal;font-weight:300;src:url(/cf-fonts/s/dm-mono/5.0.18/latin-ext/300/normal.woff2);unicode-range:U+0100-02AF,U+0304,U+0308,U+0329,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20CF,U+2113,U+2C60-2C7F,U+A720-A7FF;font-display:swap}@font-face{font-family:DM Mono;font-style:normal;font-weight:400;src:url(/cf-fonts/s/dm-mono/5.0.18/latin/400/normal.woff2);unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD;font-display:swap}@font-face{font-family:DM Mono;font-style:normal;font-weight:400;src:url(/cf-fonts/s/dm-mono/5.0.18/latin-ext/400/normal.woff2);unicode-range:U+0100-02AF,U+0304,U+0308,U+0329,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20CF,U+2113,U+2C60-2C7F,U+A720-A7FF;font-display:swap}@font-face{font-family:DM Sans;font-style:normal;font-weight:300;src:url(/cf-fonts/v/dm-sans/5.0.18/latin-ext/wght/normal.woff2);unicode-range:U+0100-02AF,U+0304,U+0308,U+0329,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20CF,U+2113,U+2C60-2C7F,U+A720-A7FF;font-display:swap}@font-face{font-family:DM Sans;font-style:normal;font-weight:300;src:url(/cf-fonts/v/dm-sans/5.0.18/latin/wght/normal.woff2);unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD;font-display:swap}@font-face{font-family:DM Sans;font-style:normal;font-weight:400;src:url(/cf-fonts/v/dm-sans/5.0.18/latin/wght/normal.woff2);unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD;font-display:swap}@font-face{font-family:DM Sans;font-style:normal;font-weight:400;src:url(/cf-fonts/v/dm-sans/5.0.18/latin-ext/wght/normal.woff2);unicode-range:U+0100-02AF,U+0304,U+0308,U+0329,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20CF,U+2113,U+2C60-2C7F,U+A720-A7FF;font-display:swap}@font-face{font-family:DM Sans;font-style:normal;font-weight:600;src:url(/cf-fonts/v/dm-sans/5.0.18/latin/wght/normal.woff2);unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD;font-display:swap}@font-face{font-family:DM Sans;font-style:normal;font-weight:600;src:url(/cf-fonts/v/dm-sans/5.0.18/latin-ext/wght/normal.woff2);unicode-range:U+0100-02AF,U+0304,U+0308,U+0329,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20CF,U+2113,U+2C60-2C7F,U+A720-A7FF;font-display:swap}</style><style>.header-logo,header::before{font-family:'Bebas Neue',sans-serif;line-height:1}.card,.card-cover,header{position:relative}.card-cover,.card-title,header{overflow:hidden}:root{--bg:#080810;--surface:#0e0e1a;--card:#111120;--border:#1c1c30;--accent:#d4a843;--accent2:#7b5ea7;--text:#dcdce8;--muted:#5a5a78;--dim:#2a2a40}*{margin:0;padding:0;box-sizing:border-box}body{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;min-height:100vh}body::after{content:'';position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.03) 2px,rgba(0,0,0,.03) 4px);pointer-events:none;z-index:9999}header{padding:40px 48px 32px;border-bottom:1px solid var(--border);display:flex;align-items:flex-end;gap:24px}header::before{content:'LIBRARY';position:absolute;right:40px;bottom:-12px;font-size:120px;color:rgba(255,255,255,.018);letter-spacing:8px;pointer-events:none}.header-logo{font-size:42px;letter-spacing:6px;color:var(--accent)}.header-sub,.read-btn{letter-spacing:2px;text-transform:uppercase}.header-count,.header-sub{font-family:'DM Mono',monospace;font-size:11px;color:var(--muted);padding-bottom:6px}.header-count{margin-left:auto}.ep-badge,.read-btn{font-size:10px;backdrop-filter:blur(4px);font-family:'DM Mono',monospace}#grid{padding:40px 48px 80px;display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:28px}.card{display:block;text-decoration:none;color:inherit;cursor:pointer;opacity:0;transform:translateY(16px);animation:.45s forwards cardIn}.card-cover{width:100%;aspect-ratio:2/3;background:var(--card);border:1px solid var(--border);border-radius:3px}.card-cover img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .5s cubic-bezier(.25, 0, 0, 1),filter .4s;filter:saturate(.85)}.card:hover .card-cover img{transform:scale(1.06);filter:saturate(1.1)}.card-cover::before{content:'';position:absolute;top:0;left:0;width:32px;height:32px;background:var(--accent);clip-path:polygon(0 0,100% 0,0 100%);z-index:2;opacity:0;transition:opacity .3s}.card:hover .card-cover::before,.card:hover .card-overlay{opacity:1}.ep-badge{position:absolute;bottom:8px;right:8px;background:rgba(8,8,16,.85);border:1px solid var(--dim);padding:3px 8px;color:var(--muted);border-radius:2px;z-index:2;transition:color .2s,border-color .2s}.card:hover .card-title,.empty-sub code,.read-btn{color:var(--accent)}.card:hover .ep-badge{color:var(--accent);border-color:rgba(212,168,67,.3)}.card-overlay{position:absolute;inset:0;background:linear-gradient(to top,rgba(8,8,16,.7) 0,transparent 60%);opacity:0;transition:opacity .35s;z-index:1;display:flex;align-items:flex-end;padding:14px}.read-btn{border:1px solid rgba(212,168,67,.6);padding:5px 12px;border-radius:2px;background:rgba(8,8,16,.6)}.empty-title,.no-thumb-label{font-family:'Bebas Neue',sans-serif}.card-cover.no-thumb{display:flex;align-items:center;justify-content:center}.no-thumb-label{font-size:13px;letter-spacing:3px;color:var(--dim);text-align:center;padding:12px;word-break:break-all;line-height:1.5}.card-info{padding:10px 2px 0}.card-title{font-size:13px;font-weight:600;color:var(--text);line-height:1.35;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;transition:color .2s}#empty{display:none;flex-direction:column;align-items:center;justify-content:center;min-height:60vh;gap:20px;text-align:center;padding:40px}#empty.show{display:flex}.empty-title{font-size:36px;letter-spacing:5px;color:var(--dim)}.empty-sub{font-size:13px;color:var(--muted);line-height:1.8;max-width:340px}.empty-sub code{font-family:'DM Mono',monospace;background:rgba(212,168,67,.08);padding:2px 6px;border-radius:3px}@keyframes cardIn{to{opacity:1;transform:translateY(0)}}@media (max-width:600px){header{padding:28px 20px 24px}#grid{padding:24px 20px 60px;gap:16px;grid-template-columns:repeat(auto-fill,minmax(140px,1fr))}}</style><header><div><div class=header-logo>MANGA</div><div class=header-sub>Offline Library</div></div><div class=header-count id=count></div></header><div id=grid></div><div id=empty><div class=empty-title>NO MANGA</div><div class=empty-sub>No data found. Run <code>python downloader.py</code> and choose Download first.</div></div><script>async function init(){let t;try{const e=await fetch("database.json");if(!e.ok)throw new Error;t=await e.json()}catch{return void document.getElementById("empty").classList.add("show")}const e=Object.entries(t);if(0!==e.length){document.getElementById("count").textContent=`${e.length} title${1!==e.length?"s":""}`;const i=document.getElementById("grid");e.forEach(([t,e],n)=>{const a=document.createElement("a");a.className="card",a.href=`index.html?manga=${encodeURIComponent(t)}&episode=1`,a.style.animationDelay=60*n+"ms";n=e.thumbnail&&""!==e.thumbnail;a.innerHTML=`<div class="card-cover${n?"":" no-thumb"}">${n?`<img src="${e.thumbnail}" alt="${e.title}" loading="lazy">`:`<div class="no-thumb-label">${e.title}</div>`}<div class="ep-badge">${e.episodes.length} eps</div><div class="card-overlay"><div class="read-btn">Read</div></div></div><div class="card-info"><div class="card-title">${e.title}</div></div>`,i.appendChild(a)})}else document.getElementById("empty").classList.add("show")}init()</script>'''

def load_db() -> dict:
    if DB_PATH.exists():
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_db(db: dict) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_key(url: str) -> str:
    u = url.rstrip('/')
    return u.split('/')[-1]

def getContentHtml(url: str) -> BeautifulSoup | None:
    try:
        response = session.get(url, headers={
            'User-Agent': user_agent,
            'Referer': url
        }, timeout=MAX_TIMEOUT)
        return BeautifulSoup(response.text, 'lxml') if response.status_code == 200 else None
    except:
        return None

def decodePattern(p: str, value: list[str]) -> str:
    def replacer(match: re.Match) -> str:
        token = match.group(0)
        idx = indexs.find(token) if len(token) == 1 else -1
        if idx != -1 and idx < len(value) and value[idx]:
            return value[idx]
        return token
    return re.sub(r'\w+', replacer, p)

def stitch_image(url: str, referer: str, pattern: list[list[str]], output_path: Path) -> None:
    res = session.get(url, headers={'User-Agent': user_agent, 'Referer': referer}, timeout=MAX_TIMEOUT)
    img = Image.open(BytesIO(res.content))
    xs = sorted(set(int(float(p[0])) for p in pattern))
    ys = sorted(set(int(float(p[1])) for p in pattern))
    tile_w = xs[1] - xs[0]
    tile_h = ys[1] - ys[0]
    width = max(xs) + tile_w
    height = max(ys) + tile_h
    canvas = Image.new('RGB', (width, height))
    for p in pattern:
        dx, dy, sx, sy = map(lambda v: int(float(v)), p)
        tile = img.crop((sx, sy, sx + tile_w, sy + tile_h))
        canvas.paste(tile, (dx, dy))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(str(output_path))

def download_plain_image(url: str, referer: str, output_path: Path) -> None:
    res = session.get(url, headers={'User-Agent': user_agent, 'Referer': referer}, timeout=MAX_TIMEOUT)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(res.content)

def download_manga(manga_url: str) -> None:
    key = get_key(manga_url)
    db = load_db()
    existing_eps = set()
    if key in db:
        existing_eps = {ep['ep'] for ep in db[key]['episodes']}
        print(f"\n[INFO] Existing data found: {db[key]['title']} ({len(existing_eps)} episodes)")
        print("[INFO] Will only download new episodes...\n")
    else:
        print(f"\n[INFO] Starting fresh download...\n")

    selectors = get_selectors(manga_url)
    if not selectors:
        print('[ERROR] No scraping configuration found for this domain.')
        return

    print('Fetching homepage...', end='', flush=True)
    homepage = getContentHtml(manga_url)
    if not homepage:
        print('\r[ERROR] Failed to fetch homepage.')
        return

    title_elem = homepage.select_one(selectors['title'])
    title = title_elem.text.strip() if title_elem else 'Unknown'

    thumb_elem = homepage.select_one(selectors['thumbnail'])
    thumbnail_url = ''
    if thumb_elem:
        thumbnail_url = thumb_elem.get('data-src') or thumb_elem.get('src')
        if thumbnail_url:
            thumbnail_url = thumbnail_url.strip()

    episodes_refs: list[dict] = []
    list_elements = homepage.select(selectors['list'])
    for chapter in list_elements:
        ep_match = re.search(r'\d+', chapter.text)
        if ep_match:
            episodes_refs.append({
                'ep': ep_match.group(),
                'link': chapter.get('href', '')
            })

    print(f'\r[OK] Homepage fetched: {title} ({len(episodes_refs)} episodes)')
    thumb_path = IMG_BASE / key / 'thumbnail.jpg'
    thumb_local = f'images/{key}/thumbnail.jpg'
    if not thumb_path.exists() and thumbnail_url:
        try:
            download_plain_image(thumbnail_url, manga_url, thumb_path)
            print(f'[OK] Thumbnail saved.')
        except Exception as e:
            print(f'[WARN] Thumbnail failed: {e}')
            thumb_local = ''

    if key not in db:
        db[key] = {'title': title, 'thumbnail': thumb_local, 'episodes': []}
    db[key]['title'] = title
    db[key]['thumbnail'] = thumb_local

    new_count = 0
    for episode_ref in reversed(episodes_refs):
        ep_num = episode_ref['ep']
        if ep_num in existing_eps:
            print(f"  [SKIP] Episode {ep_num} already exists")
            continue
        print(f"  [GET] Episode {ep_num}...", end='', flush=True)
        chapter = getContentHtml(episode_ref['link'])
        if not chapter:
            print(f"\r  [FAIL] Episode {ep_num} could not be loaded, skipping")
            continue

        local_images: list[str] = []
        content_div = chapter.select_one(selectors['tags'].rsplit(' ', 1)[0]) if ' ' in selectors['tags'] else chapter
        if not content_div:
            print(f"\r  [FAIL] Episode {ep_num} - content container not found")
            continue

        tags = content_div.find_all() if selectors['tags'].endswith('*') else content_div.select(selectors['tags'])
        raw_entries: list[dict] = []
        for tag in tags:
            if tag.name == 'img':
                raw_entries.append({'type': 'img', 'url': tag.get('src', '').strip()})
            elif tag.name == 'script':
                script = tag.string
                if script and script.startswith('eval'):
                    raw_entries.append({'type': 'script', 'script': script})

        if not raw_entries:
            for script_tag in chapter.find_all('script'):
                script_text = script_tag.string
                if script_text and 'ts_reader.run' in script_text:
                    try:
                        json_match = re.search(r'ts_reader\.run\((\{.*?\})\)', script_text, re.DOTALL)
                        if json_match:
                            data = json.loads(json_match.group(1))
                            if 'sources' in data and len(data['sources']) > 0:
                                images = data['sources'][0].get('images', [])
                                for img_url in images:
                                    raw_entries.append({'type': 'img', 'url': img_url.strip()})
                    except Exception as e:
                        print(f"\n    [WARN] Failed to parse ts_reader script: {e}")
                    break

        total = len(raw_entries)
        pad = 3 if total > 99 else 2 if total > 9 else 1
        img_dir = IMG_BASE / key / ep_num

        def download_entry(args):
            idx, entry = args
            idx_str = str(idx).zfill(pad)
            out_path = img_dir / f'{idx_str}.jpg'
            rel_path = f'images/{key}/{ep_num}/{idx_str}.jpg'
            if entry['type'] == 'img':
                try:
                    download_plain_image(entry['url'], episode_ref['link'], out_path)
                    return (idx, rel_path)
                except Exception as e:
                    print(f"\n    [WARN] Image {idx} failed: {e}")
                    return (idx, None)
            elif entry['type'] == 'script':
                try:
                    raws = {
                        'href': re.search(r"(\w+://[\w./\-]+\.\w+)", entry['script']).group(1),
                        'pattern': re.search(r"(\[\[(?:.|\n)*?\]\])", entry['script']).group(1),
                        'value': re.search(r"'(\|[^']+)'", entry['script']).group(1)
                    }
                    value = raws['value'].split('|')
                    href = decodePattern(raws['href'], value)
                    pattern = ast.literal_eval(decodePattern(raws['pattern'], value))
                    stitch_image(href, episode_ref['link'], pattern, out_path)
                    return (idx, rel_path)
                except Exception as e:
                    print(f"\n    [WARN] Stitched image error: {e}")
                    return (idx, None)
            return (idx, None)

        results = {}
        with ThreadPoolExecutor(max_workers=MAX_WORKER) as executor:
            futures = {executor.submit(download_entry, (i, e)): i for i, e in enumerate(raw_entries)}
            for future in as_completed(futures):
                idx, path = future.result()
                results[idx] = path

        local_images = [results[i] for i in sorted(results) if results[i] is not None]
        print(f"\r  [OK] Episode {ep_num} — {len(local_images)} images")
        db[key]['episodes'].append({'ep': ep_num, 'images': local_images})
        new_count += 1
        save_db(db)

    if new_count == 0:
        print("\n[INFO] All episodes already up to date.")
    else:
        print(f"\n[DONE] Downloaded {new_count} new episode(s).")

class EmbeddedHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.directory = VIEWER_DIR
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html' or self.path.startswith('/index.html?'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(INDEX_HTML.encode('utf-8'))
            return
        if self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-Type', 'image/x-icon')
            self.send_header('Content-Length', str(len(FAVICON)))
            self.end_headers()
            self.wfile.write(FAVICON)
            return
        if self.path == '/library.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(LIBRARY_HTML.encode('utf-8'))
            return
        if self.path == '/database.json' or self.path.startswith('/images/'):
            if self.path == '/database.json':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                with open(DB_PATH, 'rb') as f:
                    self.wfile.write(f.read())
                return
            super().do_GET()
            return
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(INDEX_HTML.encode('utf-8'))

    def log_message(self, format, *args):
        pass

def kill_port(port: int) -> None:
    """Kill process using given port via /proc/net/tcp (no root needed)."""
    import signal, time

    def _hex_port(p):
        return f'{p:04X}'

    try:
        target_hex = _hex_port(port)
        inode_set = set()

        for tcp_file in ('/proc/net/tcp', '/proc/net/tcp6'):
            try:
                with open(tcp_file, 'r') as f:
                    for line in f.readlines()[1:]:
                        parts = line.split()
                        if len(parts) < 10:
                            continue
                        local_port_hex = parts[1].split(':')[1]
                        if local_port_hex.upper() == target_hex:
                            inode_set.add(parts[9])
            except (PermissionError, FileNotFoundError):
                continue

        if not inode_set:
            return

        for pid_str in os.listdir('/proc'):
            if not pid_str.isdigit():
                continue
            fd_dir = f'/proc/{pid_str}/fd'
            try:
                for fd in os.listdir(fd_dir):
                    try:
                        link = os.readlink(f'{fd_dir}/{fd}')
                        if link.startswith('socket:[') and link[8:-1] in inode_set:
                            os.kill(int(pid_str), signal.SIGTERM)
                            time.sleep(0.5)
                            return
                    except (PermissionError, FileNotFoundError, OSError):
                        continue
            except (PermissionError, FileNotFoundError):
                continue
    except Exception:
        pass

class ReusableHTTPServer(http.server.HTTPServer):
    allow_reuse_address = True

def start_server() -> None:
    viewer_dir = VIEWER_DIR
    viewer_dir.mkdir(exist_ok=True)
    os.chdir(viewer_dir)
    kill_port(PORT)
    server = ReusableHTTPServer(('', PORT), EmbeddedHandler)
    print(f'\nServer running at http://localhost:{PORT}')
    print('   Press Ctrl+C to stop\n')
    webbrowser.open(f'http://localhost:{PORT}/library.html')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print('\nServer stopped.')
        exit(1)

async def menu_async() -> None:
    intro('Manga Offline Reader')
    choice = await select(
        'Select progress:',
        options=[
            Option('download', 'Download / Update Manga'),
            Option('read',     'Start Read (offline)'),
            Option('exit',     'Exit'),
        ]
    )
    if choice == 'download':
        url = await text(
            'Manhuathai URL:',
            placeholder='https://www.manhuathai.com/manga/...',
            validate=lambda v: 'Please type URL' if not v.strip() else None
        )
        outro('')
        download_manga(url.strip())
        await menu_async()
    elif choice == 'read':
        db = load_db()
        if not db:
            outro('[ERROR] No data found. Please download first.')
        else:
            outro('Starting server...')
            start_server()
    else:
        outro('Bye!')

def menu() -> None:
    asyncio.run(menu_async())

def main():
    subprocess.run('cls' if os.name == 'nt' else 'clear', shell=True)
    print()
    menu()

if __name__ == '__main__':
    main()
