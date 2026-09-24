#!/usr/bin/env python3
"""
Fetch US official heat-related deaths (ICD-10 underlying cause X30, "Exposure to
excessive natural heat") by year from CDC WONDER, for context on the
under-ascription of heat in crash mortality.

CDC WONDER Underlying Cause of Death, 1999-2020 (database D76), API endpoint
https://wonder.cdc.gov/controller/datarequest/D76 . Result saved to
data/processed/cdc_heat_deaths.csv with the exact query for reproducibility.
"""
import os
import urllib.request
import xml.etree.ElementTree as ET
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PROC = os.path.join(os.path.dirname(HERE), "data", "processed")
URL = "https://wonder.cdc.gov/controller/datarequest/D76"


def param(name, *values):
    s = f"<parameter>\n<name>{name}</name>\n"
    for v in values:
        s += f"<value>{v}</value>\n"
    return s + "</parameter>\n"


def build_xml():
    P = [
        ("B_1", "D76.V1-level1"), ("B_2", "*None*"), ("B_3", "*None*"),
        ("B_4", "*None*"), ("B_5", "*None*"),
        ("M_1", "D76.M1"), ("M_2", "D76.M2"), ("M_3", "D76.M3"),
        ("F_D76.V1", "*All*"), ("F_D76.V10", "*All*"), ("F_D76.V2", "X30"),
        ("F_D76.V27", "*All*"), ("F_D76.V9", "*All*"),
        ("I_D76.V1", "*All* (All Dates)"), ("I_D76.V10", "*All* (The United States)"),
        ("I_D76.V2", "X30 (Exposure to excessive natural heat)"),
        ("I_D76.V27", "*All* (The United States)"), ("I_D76.V9", "*All* (The United States)"),
        ("O_V1_fmode", "freg"), ("O_V27_fmode", "freg"), ("O_V2_fmode", "freg"),
        ("O_V9_fmode", "freg"), ("O_V10_fmode", "freg"),
        ("O_aar", "aar_none"), ("O_aar_pop", "0000"),
        ("O_age", "D76.V5"), ("O_javascript", "on"), ("O_location", "D76.V9"),
        ("O_precision", "1"), ("O_rate_per", "100000"), ("O_show_totals", "true"),
        ("O_timeout", "600"), ("O_title", "heat X30 by year"), ("O_ucd", "D76.V2"),
        ("O_urban", "D76.V19"),
        ("V_D76.V1", ""), ("V_D76.V10", ""), ("V_D76.V11", "*All*"),
        ("V_D76.V12", "*All*"), ("V_D76.V17", "*All*"), ("V_D76.V19", "*All*"),
        ("V_D76.V2", ""), ("V_D76.V20", "*All*"), ("V_D76.V21", "*All*"),
        ("V_D76.V22", "*All*"), ("V_D76.V23", "*All*"), ("V_D76.V24", "*All*"),
        ("V_D76.V25", "*All*"), ("V_D76.V27", ""), ("V_D76.V4", "*All*"),
        ("V_D76.V5", "*All*"), ("V_D76.V51", "*All*"), ("V_D76.V52", "*All*"),
        ("V_D76.V6", "00"), ("V_D76.V7", "*All*"), ("V_D76.V8", "*All*"),
        ("V_D76.V9", ""),
    ]
    p = "<request-parameters>\n"
    p += param("accept_datause_restrictions", "true")
    for k, v in P:
        p += param(k, v)
    p += "</request-parameters>"
    return p


def main():
    raw = os.path.join(os.path.dirname(PROC), "raw", "cdc_wonder_D76_X30.xml")
    if os.path.exists(raw):
        txt = open(raw).read()
    else:
        data = urllib.parse.urlencode({"request_xml": build_xml(),
                                       "accept_datause_restrictions": "true"}).encode()
        txt = urllib.request.urlopen(urllib.request.Request(URL, data=data), timeout=600).read().decode()
        open(raw, "w").write(txt)
    root = ET.fromstring(txt)
    rows = []
    for r in root.iter("r"):
        cells = list(r.iter("c"))
        lab = cells[0].get("l")
        if lab and lab.isdigit() and len(lab) == 4:      # a Year row
            deaths = int(cells[1].get("v").replace(",", ""))
            rows.append((int(lab), deaths))
    df = pd.DataFrame(rows, columns=["year", "heat_deaths_X30"]).sort_values("year")
    df.to_csv(os.path.join(PROC, "cdc_heat_deaths.csv"), index=False)
    print(df.to_string(index=False))
    print("mean 2016-2020:", round(df[df.year.between(2016, 2020)].heat_deaths_X30.mean(), 1))


if __name__ == "__main__":
    import urllib.parse
    main()
