"""Monte Carlo прогноз кількості спринтів до закриття обсягу (ЛР9).

Приклади:
    python lr09_forecast/simulate.py 220 --csv шлях/до/lr09_reference_velocity.csv
    python lr09_forecast/simulate.py 220 --csv ref.csv --sprints 1,2
    python lr09_forecast/simulate.py 42 --csv lr09_forecast/velocity.csv
"""
import argparse
import csv
import math
import random


def load_velocity(path, sprints=None):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [int(r["points_done"]) for r in rows
            if sprints is None or int(r["sprint"]) in sprints]


def simulate(points, history, runs, seed):
    rng = random.Random(seed)
    results = []
    for _ in range(runs):
        left, sprints = points, 0
        while left > 0:
            left -= rng.choice(history)
            sprints += 1
            if sprints > 1000:  # уся історія з нулів: обсяг не закривається ніколи
                break
        results.append(sprints)
    results.sort()
    return results


def percentile(sorted_results, q):
    # найменше число, нижче або на рівні якого лежить q частка результатів
    return sorted_results[math.ceil(q * len(sorted_results)) - 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("points", type=int, help="обсяг, який треба закрити")
    ap.add_argument("--csv", required=True, help="файл із колонками sprint і points_done")
    ap.add_argument("--sprints", help="які спринти брати, через кому; за замовчуванням усі")
    ap.add_argument("--runs", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    chosen = {int(s) for s in a.sprints.split(",")} if a.sprints else None
    history = load_velocity(a.csv, chosen)
    res = simulate(a.points, history, a.runs, a.seed)
    p50, p85 = percentile(res, 0.50), percentile(res, 0.85)
    print(f"velocity={history} points={a.points} runs={a.runs}")
    print(f"P50={p50} P85={p85} ширина={p85 - p50}")


if __name__ == "__main__":
    main()
