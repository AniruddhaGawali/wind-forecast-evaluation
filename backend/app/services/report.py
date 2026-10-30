"""Print the full analysis for the saved data. Run with `python -m app.services.report [--cutoff 09:00]`."""

import argparse

from app.config import DEFAULT_CUTOFF, DELIVERY_END, DELIVERY_START, SENSITIVITY_CUTOFFS
from app.services import metrics
from app.services.data_store import load_data
from app.services.selection import build_scored, parse_cutoff


def _fmt(value: object) -> str:
    return f"{value:,.0f}" if isinstance(value, float) else str(value)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cutoff", default=DEFAULT_CUTOFF, help="decision time on D-1, UK time (HH:MM)"
    )
    args = parser.parse_args()

    store = load_data()
    cutoff = parse_cutoff(args.cutoff)
    scored, coverage = build_scored(
        store.actuals, store.forecasts, cutoff, DELIVERY_START, DELIVERY_END
    )
    summary = metrics.summarise(scored)

    print(
        f"=== Cutoff {args.cutoff} UK on D-1, delivery {DELIVERY_START} to {DELIVERY_END} ==="
    )
    print(f"Coverage: {coverage}")
    print(
        "Summary (MW): "
        + ", ".join(f"{k}={_fmt(v)}" for k, v in summary.as_dict().items())
    )
    print(metrics.recommendation_text(summary.p90))
    for title, rows in [
        ("By horizon", metrics.by_horizon(scored)),
        ("By generation level", metrics.by_generation_level(scored)),
        ("By hour of day (UTC)", metrics.by_hour_of_day(scored)),
    ]:
        print(f"\n{title}:")
        for row in rows:
            print(
                "  "
                + ", ".join(
                    f"{k}={_fmt(v)}"
                    for k, v in row.items()
                    if k in row and k not in {"p50", "p95"}
                )
            )

    print("\nSensitivity:")
    for value in SENSITIVITY_CUTOFFS:
        s, c = build_scored(
            store.actuals,
            store.forecasts,
            parse_cutoff(value),
            DELIVERY_START,
            DELIVERY_END,
        )
        m = metrics.summarise(s)
        print(
            f"  {value}: scored={c.scored}/{c.expected} mae={_fmt(m.mae)} rmse={_fmt(m.rmse)} "
            f"bias={_fmt(m.bias)} p90={_fmt(m.p90)} wape={m.wape_pct:.1f}%"
        )


if __name__ == "__main__":
    main()
