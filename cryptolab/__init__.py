"""Simulate integer reserve swaps, liquidity minting, fees and price impact without RPC access."""

import json


def positive(value):
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError("positive integer required")
    return value


def quote(amount, reserve_in, reserve_out, fee_bps=30):
    positive(amount)
    positive(reserve_in)
    positive(reserve_out)
    if not isinstance(fee_bps, int) or not 0 <= fee_bps < 10000:
        raise ValueError("invalid fee")
    effective = amount * (10000 - fee_bps)
    return effective * reserve_out // (reserve_in * 10000 + effective)


def analyze(data):
    import math

    x = positive(data["reserve_x"])
    y = positive(data["reserve_y"])
    supply = positive(data["lp_supply"])
    fee = data.get("fee_bps", 30)
    if not isinstance(fee, int) or not 0 <= fee < 10000:
        raise ValueError("invalid fee")
    history = []
    for action in data["actions"]:
        before = x * y
        kind = action["type"]
        if kind == "swap":
            amount = positive(action["amount"])
            direction = action["direction"]
            if direction == "x_to_y":
                output = quote(amount, x, y, fee)
                x += amount
                y -= output
            elif direction == "y_to_x":
                output = quote(amount, y, x, fee)
                y += amount
                x -= output
            else:
                raise ValueError("invalid direction")
            if output <= 0 or output < action.get("min_output", 0):
                raise ValueError("slippage or dust output")
            event = {"output": output}
        elif kind == "add_liquidity":
            dx = positive(action["amount_x"])
            dy = positive(action["amount_y"])
            minted = min(dx * supply // x, dy * supply // y)
            if minted == 0:
                raise ValueError("dust liquidity")
            used_x = (minted * x + supply - 1) // supply
            used_y = (minted * y + supply - 1) // supply
            x += used_x
            y += used_y
            supply += minted
            event = {"minted": minted, "refund_x": dx - used_x, "refund_y": dy - used_y}
        elif kind == "remove_liquidity":
            burn = positive(action["shares"])
            if burn >= supply:
                raise ValueError("must retain pool liquidity")
            dx = burn * x // supply
            dy = burn * y // supply
            x -= dx
            y -= dy
            supply -= burn
            event = {"amount_x": dx, "amount_y": dy}
        else:
            raise ValueError("unknown action")
        history.append(
            {
                "type": kind,
                **event,
                "reserve_x": x,
                "reserve_y": y,
                "k": x * y,
                "k_before": before,
                "lp_supply": supply,
            }
        )
    return {"reserve_x": x, "reserve_y": y, "lp_supply": supply, "history": history}


import argparse
import csv
import io
import sys
from pathlib import Path


def load_input(path):
    raw = Path(path).read_text(encoding="utf-8")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError("invalid JSON constant: " + value)

    data = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid_constant)
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON object")
    return data


def flatten(value, prefix=""):
    rows = []
    if isinstance(value, dict):
        for key, item in value.items():
            rows.extend(flatten(item, f"{prefix}.{key}" if prefix else key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            rows.extend(flatten(item, f"{prefix}[{index}]"))
    else:
        rows.append((prefix, json.dumps(value, ensure_ascii=False)))
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="JSON input file")
    parser.add_argument("--output", help="write result atomically to a file")
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    args = parser.parse_args(argv)
    try:
        result = analyze(load_input(args.input))
        if args.format == "json":
            content = (
                json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
            )
        else:
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(["path", "value"])
            writer.writerows(flatten(result))
            content = buffer.getvalue()
        if args.output:
            import os, tempfile

            target = Path(args.output)
            fd, temporary = tempfile.mkstemp(
                prefix="." + target.name + ".", dir=target.parent
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as stream:
                    stream.write(content)
                os.replace(temporary, target)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        else:
            sys.stdout.write(content)
    except (ValueError, KeyError, TypeError, OSError, ArithmeticError) as error:
        parser.exit(2, f"error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
