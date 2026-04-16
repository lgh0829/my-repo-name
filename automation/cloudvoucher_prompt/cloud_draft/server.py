"""
PatSol 클라우드바우처 초안 생성 서버
실행: python server.py
접속: http://localhost:8000
"""

import logging
import os
import sys
import traceback
from pathlib import Path
from urllib.parse import quote

logging.basicConfig(level=logging.INFO)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# os.environ["OPENAI_API_KEY"] = ""  # 환경변수로 설정하세요

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PatSol 클라우드바우처 초안 생성기")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_PATH = Path(__file__).parent / "survey_form.html"


@app.get("/", response_class=HTMLResponse)
async def form():
    return HTML_PATH.read_text(encoding="utf-8")


@app.post("/api/generate")
async def generate(request: Request):
    survey = await request.json()

    try:
        from cloud_draft import CloudDraft2026
        draft = CloudDraft2026()
        paths = await draft.make_draft(survey)
    except Exception as e:
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

    if not paths:
        raise HTTPException(status_code=500, detail="파일 생성에 실패했습니다.")

    file_path = paths[0]
    filename = Path(file_path).name
    encoded_name = quote(filename, safe="")

    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_name}"
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=11000, reload=True)
