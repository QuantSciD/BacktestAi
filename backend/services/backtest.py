import os
from typing import Dict, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def compute_backtest_metrics(prices: pd.Series) -> Dict:
    returns = prices.pct_change().dropna()

    total_return = float((prices.iloc[-1] / prices.iloc[0]) - 1.0)
    vol = float(returns.std())
    sharpe = float(total_return / vol) if vol != 0 else 0.0

    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = cumulative / running_max - 1
    max_drawdown = float(drawdown.min())

    metrics = {
        "total_return": total_return,
        "volatility": vol,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
        "n_points": int(len(prices)),
    }
    return metrics


def basic_bias_flags(metrics: Dict) -> List[str]:
    flags: List[str] = []
    if metrics["n_points"] < 50:
        flags.append("Sample size is small; results may be unreliable.")
    if metrics["sharpe"] > 3.0:
        flags.append("Sharpe ratio is very high; potential overfitting.")
    if metrics["max_drawdown"] > -0.02:
        flags.append("Very low drawdown; may indicate unrealistic data or overfitting.")
    return flags


def generate_equity_curve_plot(prices: pd.Series, out_path: str) -> str:
    returns = prices.pct_change().dropna()
    equity = (1 + returns).cumprod()

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    plt.figure(figsize=(8, 4))
    plt.plot(equity.index, equity.values, label="Equity curve")
    plt.xlabel("Time")
    plt.ylabel("Equity (normalized)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

    return out_path
