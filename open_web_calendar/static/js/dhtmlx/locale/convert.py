# SPDX-FileCopyrightText: 2024 Nicco Kunzmann and Open Web Calendar Contributors <https://open-web-calendar.quelltext.eu/>
#
# SPDX-License-Identifier: GPL-2.0-only
"""Script to convert the DHTMLX calendar translations for yaml files."""

import os
import re

regex = re.compile(r"\{[^{]*(\{.*\})\}", re.DOTALL | re.MULTILINE)

date = "date"
month_full = "month_full:"

en = {}

M = "jan feb mar apr may jun jul aug sep oct nov dec".split()  # noqa: RUF100, SIM905
D = "sun mon tue wed thu fri sat".split()  # noqa: RUF100, SIM905


def used(s):
    return (
        s.startswith("date_")
        or (
            s.startswith("labels_")
            and not any(
                x in s
                for x in "repeat drag message button icon new confirm section "  # noqa: RUF100, SIM905
                "select recurring labels_year_tab labels_grid_tab"
                "labels_full_day".split()
            )
        )
        or s
        in """
    labels_dhx_cal_today_button
    """
    )


def add(l, v):  # noqa: E741
    global yaml  # noqa: PLW0603
    k = "_".join(l)
    # sanitize
    #    v = v.strip()
    assert '"' not in v
    v = '"' + v.replace("=", ":") + '"'
    if v == "":
        v = '""'
    # check translated
    if lang == "en":
        en[k] = v
    elif en.get(k) == v:
        print(f"skip {k} is english: {v}")
        return
    if not used(k):
        #        print(f"Not used {k}")
        yaml += "#: not used in this project\n"
    yaml += f"{k}: {v}\n"


for file in ["locale_en.js"] + os.listdir("."):  # noqa: PTH208, RUF100
    if not file.endswith(".js"):
        continue
    lang = file[file.index("_") + 1 : file.index(".")]
    print(f" ----- {lang} ----- ")
    with open(file) as f:
        r = regex.findall(f.read())
    assert len(r) == 1, r
    # Parse the JS object without eval — eval on file content is escapable
    # via __subclasses__ chains. Quote bare keys, then ast.literal_eval.
    import ast
    js_obj = r[0]
    py_obj = re.sub(r'([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:', r'\1"\2":', js_obj)
    py_obj = re.sub(r"\btrue\b", "True", py_obj)
    py_obj = re.sub(r"\bfalse\b", "False", py_obj)
    py_obj = re.sub(r"\bnull\b", "None", py_obj)
    r = ast.literal_eval(py_obj)
    print(list(r))
    print(r)
    yaml = ""
    for x in ["month_full", "month_short"]:
        for k, v in zip(M, r["date"][x], strict=False):
            add(["date", x, k], v)
    for x in ["day_full", "day_short"]:
        for k, v in zip(D, r["date"][x], strict=False):
            if x == "day_full" and lang == "el" and k == "sat" and v == "Κυριακή":
                # https://github.com/niccokunzmann/open-web-calendar/commit/670b6a7587a3b6bc730301bf288b31afb760d419
                v = "Σάββατο"
            add(["date", x, k], v)
    for k, v in r["labels"].items():
        if not isinstance(v, str):
            assert k in ["month_for_recurring", "day_for_recurring"], v  # checked below
            continue
        add(["labels", k], v)
    if "month_for_recurring" in r["labels"]:
        for k, v in zip(M, r["labels"]["month_for_recurring"], strict=False):
            add(["labels", "month_for_recurring", k], v)
    if "day_for_recurring" in r["labels"]:
        for k, v in zip(D, r["labels"]["day_for_recurring"], strict=False):
            add(["labels", "day_for_recurring", k], v)
    print(yaml)
    directory = "../../../../translations/" + lang
    os.makedirs(directory, exist_ok=True)
    with open(directory + "/calendar.yml", "w") as f:
        f.write(yaml)
