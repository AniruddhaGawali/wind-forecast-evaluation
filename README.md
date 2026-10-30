# Wind Forecast Evaluation Portal

[![CI](https://github.com/AniruddhaGawali/wind-forecast-evaluation/actions/workflows/ci.yml/badge.svg)](https://github.com/AniruddhaGawali/wind-forecast-evaluation/actions/workflows/ci.yml)

How wrong was the day-ahead GB wind forecast you could have used? This portal compares national GB wind output with the forecast available at a chosen decision time on the day before, for deliveries from 2 January to 1 February 2026, and turns the misses into a buffer recommendation.

## Run it

```bash
docker compose up --build
```

- Dashboard: http://localhost:3000
- API docs: http://localhost:8000/docs

## Use of AI tools

Parts of this project were written with the help of Claude Code (an AI coding assistant).
