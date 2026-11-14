"""Forecast Bitcoin's US-dollar price 240 minutes after a checkpoint.

Reads every case file in the input directory, each holding 4,320
one-minute closes for the 72 hours up to a checkpoint, and writes one
forecast per case to the output directory.

Forecasting idea, in plain words: start from the last known price.
Look at how the price has been drifting lately: the typical
minute-to-minute change over the last hour (a median, so single wild
minutes do not dominate) and the total move of the last hour spread
over its sixty minutes. Blend those two drift readings, project them
240 minutes forward, but shrink the projection hard, because most of
a one-hour move does not keep going for four hours. Finally, cap the
whole move at twice the typical four-hour move seen over the last
three days, so a freak hour can never throw the forecast far away.
When the recent drift is flat, the forecast simply stays near the
last price. Everything is deterministic: no network, no clock, no
randomness, standard library only.
"""

import json
import os
import statistics


def median(values):
    return statistics.median(values)


def forecast(prices):
    last = prices[-1]
    if len(prices) < 61:
        return last
    changes = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    typical_minute_move = median(changes[-60:])
    last_hour_move_per_minute = (last - prices[-61]) / 60.0
    drift = typical_minute_move + 0.5 * last_hour_move_per_minute
    move = drift * 240.0 * 0.3
    four_hour_moves = [
        abs(prices[j] - prices[j - 240]) for j in range(240, len(prices))
    ]
    cap = 2.0 * median(four_hour_moves)
    if move > cap:
        move = cap
    elif move < -cap:
        move = -cap
    guess = last + move
    if guess <= 0:
        guess = last
    return guess


def main():
    input_dir = os.environ.get("MAKEFUN_INPUT_DIR") or "/input"
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(output_dir, exist_ok=True)
    names = sorted(
        name for name in os.listdir(input_dir) if name.endswith(".in")
    )
    for name in names:
        with open(os.path.join(input_dir, name), "r", encoding="utf-8") as handle:
            case = json.load(handle)
        case_id = case["case"]
        prices = case["markets"][0]["prices"]
        guess = forecast(prices)
        # Round to whole cents: the price grid itself moves in cents,
        # and extra decimals carry no information.
        guess = round(guess, 2)
        payload = {"forecasts": [{"case": case_id, "price": guess}]}
        out_name = name[:-3] + ".out"
        with open(
            os.path.join(output_dir, out_name), "w", encoding="utf-8"
        ) as handle:
            handle.write(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
