import io
import os
from typing import List

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import Upload, BacktestRun, Suggestion
from .services.backtest import (
    compute_backtest_metrics,
    generate_equity_curve_plot,
    basic_bias_flags,
)
from .services.llm import generate_experiment_suggestions



Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PLOTS_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)
app.mount("/plots", StaticFiles(directory=PLOTS_DIR), name="plots")


class SuggestionOut(BaseModel):
    title: str
    description: str
    risk_note: str | None = None


class BacktestResponse(BaseModel):
    metrics: dict
    plot_url: str | None
    suggestions: List[SuggestionOut]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/backtest", response_model=BacktestResponse)
async def backtest(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    if "price" not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must have a 'price' column.")

    prices = df["price"].astype(float)

    metrics = compute_backtest_metrics(prices)
    flags = basic_bias_flags(metrics)

    upload = Upload(filename=file.filename)
    db.add(upload)
    db.commit()
    db.refresh(upload)

    plot_path = os.path.join(PLOTS_DIR, f"equity_{upload.id}.png")
    generate_equity_curve_plot(prices, plot_path)
    plot_url = f"/plots/equity_{upload.id}.png"

    backtest_run = BacktestRun(
        upload_id=upload.id,
        metrics=metrics,
        equity_curve_path=plot_path,
    )
    db.add(backtest_run)
    db.commit()
    db.refresh(backtest_run)

    suggestions_raw = generate_experiment_suggestions(metrics, flags)
    suggestions_out: List[SuggestionOut] = []

    for s in suggestions_raw[:3]:
        sug = Suggestion(
            backtest_run_id=backtest_run.id,
            title=s.get("title", "Untitled"),
            description=s.get("description", ""),
            risk_note=s.get("risk_note"),
        )
        db.add(sug)
        db.commit()
        db.refresh(sug)

        suggestions_out.append(
            SuggestionOut(
                title=sug.title,
                description=sug.description,
                risk_note=sug.risk_note,
            )
        )

    return BacktestResponse(
        metrics=metrics,
        plot_url=plot_url,
        suggestions=suggestions_out,
    )
