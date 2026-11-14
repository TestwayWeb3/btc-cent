# BTC cent forecast 01

This entry forecasts Bitcoin's US-dollar price 240 minutes after each
checkpoint, from the 4,320 one-minute closes of the 72 hours up to
that checkpoint.

How it forecasts: it starts from the last known price and adds a
heavily shrunk projection of the recent drift. The drift blends two
readings of the last hour — the typical minute-to-minute change (a
median, so single wild minutes do not dominate) and the last hour's
total move spread over its sixty minutes — projected 240 minutes
forward at a small fraction of its full size, because most of a
one-hour move does not keep going for four hours. The whole move is
capped at twice the typical four-hour move seen over the last three
days, so a freak hour can never throw the forecast far away. When
recent drift is flat, the forecast stays near the last price.

The program uses only the Python standard library, is fully
deterministic, and uses no network, no clock, and no randomness.
