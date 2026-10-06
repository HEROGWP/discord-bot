"""把公開 Google 試算表的指定範圍匯出成 PNG。

單獨執行可產生預覽圖：python sheet_snapshot.py R31:AG64
"""
import asyncio
import io
import os
import sys

import aiohttp
import pymupdf
from dotenv import load_dotenv
from PIL import Image, ImageChops

SHEET_GID = 0

# 匯出 PDF 的縮放倍率，3 倍約 216 DPI
RENDER_ZOOM = 3
# 裁掉空白後保留的邊距（px）
PADDING = 20


def export_url(cell_range):
    return (
        f'https://docs.google.com/spreadsheets/d/{os.environ["SHEET_ID"]}/export'
        f'?format=pdf&gid={SHEET_GID}&range={cell_range}'
        '&gridlines=false&portrait=false&fitw=true&size=A4'
        '&top_margin=0&bottom_margin=0&left_margin=0&right_margin=0'
    )


async def fetch_pdf(cell_range):
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(export_url(cell_range)) as resp:
            resp.raise_for_status()
            if resp.content_type != 'application/pdf':
                # 試算表不是公開時，Google 會回傳登入頁 HTML
                raise RuntimeError(f'預期取得 PDF，實際為 {resp.content_type}，試算表可能不是公開的')
            return await resp.read()


def pdf_to_png(pdf_bytes):
    with pymupdf.open(stream=pdf_bytes, filetype='pdf') as doc:
        pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(RENDER_ZOOM, RENDER_ZOOM), alpha=False)
        image = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)

    # 裁掉 PDF 頁面周圍的空白
    background = Image.new('RGB', image.size, (255, 255, 255))
    bbox = ImageChops.difference(image, background).getbbox()
    if bbox:
        left, top, right, bottom = bbox
        image = image.crop((
            max(left - PADDING, 0),
            max(top - PADDING, 0),
            min(right + PADDING, image.width),
            min(bottom + PADDING, image.height),
        ))

    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


async def capture(cell_range):
    """回傳試算表指定範圍（例如 'A31:P64'）的 PNG bytes。"""
    pdf_bytes = await fetch_pdf(cell_range)
    return await asyncio.to_thread(pdf_to_png, pdf_bytes)


if __name__ == '__main__':
    load_dotenv()
    cell_range = sys.argv[1] if len(sys.argv) > 1 else 'A31:P64'
    png = asyncio.run(capture(cell_range))
    with open('sheet.png', 'wb') as f:
        f.write(png)
    print(f'已儲存 sheet.png（{len(png)} bytes）')
