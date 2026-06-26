"""
ETF universe across TSX, TSX Venture, NEO/Cboe Canada, NYSE, and NASDAQ.
Canadian ETFs use the .TO suffix (yfinance standard for TSX/NEO-listed securities).
Tickers that fail to download or lack sufficient history are silently dropped at runtime.
"""
from __future__ import annotations
from typing import List

# ── Canadian ETFs ─────────────────────────────────────────────────────────────

ISHARES_CA = [
    "XIU.TO", "XIC.TO", "XSP.TO", "XUS.TO", "XEF.TO", "XEM.TO",
    "XEQT.TO", "XGRO.TO", "XBAL.TO", "XCNS.TO", "XINC.TO",
    "XBB.TO", "XCB.TO", "XGB.TO", "XRB.TO", "XSB.TO", "XHB.TO",
    "XRE.TO", "XFN.TO", "XEG.TO", "XMA.TO", "XIT.TO", "XHC.TO",
    "XUT.TO", "XST.TO", "XTR.TO", "XDIV.TO", "XEI.TO", "XDV.TO",
    "XDIV.TO",
]

VANGUARD_CA = [
    "VFV.TO", "VCN.TO", "VXC.TO", "VEQT.TO", "VGRO.TO", "VBAL.TO",
    "VCNS.TO", "VCIP.TO", "VAB.TO", "VSB.TO", "VSC.TO", "VUN.TO",
    "VUS.TO", "VIU.TO", "VEE.TO", "VRE.TO", "VDU.TO", "VIDY.TO",
    "VBU.TO", "VBG.TO",
]

BMO_CA = [
    "ZSP.TO", "ZCN.TO", "ZAG.TO", "ZGRO.TO", "ZBAL.TO", "ZLB.TO",
    "ZRE.TO", "ZFN.TO", "ZEB.TO", "ZEO.TO", "ZWC.TO", "ZWH.TO",
    "ZWE.TO", "ZWA.TO", "ZWB.TO", "ZDV.TO", "ZPR.TO", "ZUB.TO",
    "ZUH.TO", "ZUT.TO", "ZWU.TO", "ZMI.TO", "ZLU.TO", "ZEM.TO",
    "ZHY.TO", "ZDB.TO", "ZPS.TO", "ZMP.TO", "ZQB.TO", "ZESG.TO",
    "ZUAG.TO", "ZMU.TO", "ZBK.TO", "ZID.TO",
]

HORIZONS_CA = [
    "HXT.TO", "HXS.TO", "HXQ.TO", "HXEM.TO", "HBB.TO", "HSAV.TO",
    "HXDM.TO", "HBAL.TO", "HGRO.TO",
]

HAMILTON_CA = [
    "HMAX.TO", "HCAL.TO", "HUTS.TO", "HDIV.TO", "HYLD.TO",
]

HARVEST_CA = [
    "HBF.TO", "HTA.TO", "HLIF.TO", "HHL.TO", "HRIF.TO",
]

TD_CA = [
    "TGRO.TO", "TBAL.TO", "TCON.TO",
]

EVOLVE_CA = [
    "ETHI.TO", "CYBR.TO", "EARN.TO", "HERO.TO", "ESPX.TO", "CALL.TO",
    "EDGE.TO", "BKCI.TO",
]

PURPOSE_CA = [
    "PSA.TO", "PHR.TO", "PDF.TO", "PFC.TO",
]

MACKENZIE_CA = [
    "MXUS.TO", "MQCA.TO", "MCSB.TO", "MCSG.TO",
]

CI_CA = [
    "CINC.TO", "FHG.TO", "FUD.TO",
]

FIDELITY_CA = [
    "FCRR.TO", "FCIQ.TO", "FUSD.TO",
]

MANULIFE_CA = [
    "MCSM.TO",
]

# ── US ETFs (NYSE / NASDAQ) ───────────────────────────────────────────────────

BROAD_US = [
    "SPY", "IVV", "VOO", "VTI", "SCHX", "SCHB", "ITOT", "IWB", "SPLG", "RSP",
]

NASDAQ = [
    "QQQ", "QQQM", "ONEQ",
]

INTL_DEVELOPED = [
    "EFA", "IEFA", "VEA", "SPDW", "SCHF",
    "EWJ", "EWG", "EWU", "EWA", "EWC", "EWQ", "EWI", "EWD", "EWL",
    "EWP", "EWN", "EWO", "EWK", "EWM", "EWS", "EWH", "EWT", "EWY",
]

EMERGING_MARKETS = [
    "EEM", "IEMG", "VWO", "SCHE",
    "EWZ", "INDA", "MCHI", "VNM", "EWW",
]

GLOBAL = [
    "ACWI", "ACWX", "VT", "URTH",
]

SECTOR_SPDR = [
    "XLK", "XLF", "XLE", "XLV", "XLI", "XLU", "XLP", "XLY", "XLB", "XLC", "XLRE",
]

SECTOR_VANGUARD = [
    "VGT", "VHT", "VFH", "VDE", "VIS", "VCR", "VDC", "VAW", "VPU", "VOX",
]

SECTOR_SPECIFIC = [
    "SOXX", "SMH",          # semiconductors
    "IGV", "SKYY", "CLOU",  # software / cloud
    "CIBR", "HACK",         # cybersecurity
    "IBB", "XBI",           # biotech
    "KRE", "KBE",           # regional / broad banks
    "GDX", "GDXJ",          # gold miners
    "OIH",                  # oil services
    "IYR", "VNQ", "SCHH",   # real estate
    "JETS",                 # airlines
]

THEMATIC = [
    "ARKK", "ARKG", "ARKF", "ARKQ", "ARKW",
    "ICLN", "QCLN", "TAN", "FAN",
    "LIT", "REMX",
    "BOTZ", "ROBO",
]

FIXED_INCOME = [
    # Treasuries
    "BIL", "SHV", "SHY", "IEI", "IEF", "TLT", "EDV",
    # Aggregate
    "AGG", "BND", "BNDX", "BNDW",
    # Corporate
    "LQD", "VCIT", "VCSH",
    # High Yield
    "HYG", "JNK",
    # Emerging Market
    "EMB", "VWOB",
    # Municipal
    "MUB", "VTEB",
    # Ultra Short
    "JPST", "MINT",
    # TIPS
    "TIP", "SCHP", "VTIP",
]

COMMODITIES = [
    "GLD", "IAU", "SLV", "PDBC", "DBC", "USO", "UNG", "GSG",
    "CORN", "WEAT", "SOYB",
]

DIVIDEND = [
    "VYM", "DVY", "SCHD", "HDV", "SDY", "VIG", "DGRO",
]

FACTOR = [
    "USMV", "EFAV", "EEMV",  # minimum volatility
    "QUAL",                   # quality
    "MTUM",                   # momentum
]

SIZE = [
    "IWM", "IJR", "SCHA",       # small cap
    "MDY", "VO", "IJH", "SCHM", # mid cap
    "IWD", "IWF",               # Russell 1000 value/growth
    "IWN", "IWO",               # Russell 2000 value/growth
    "VTV", "VUG", "IVE", "IVW", # value / growth
]

# Single-inverse ETFs (-1x only — no leverage decay).
# These pass the vol screen during bear markets and act as natural hedges.
# Leveraged inverse (-2x, -3x) are intentionally excluded: daily rebalancing
# causes volatility decay that destroys long-term value.
INVERSE = [
    "SH",   # ProShares Short S&P 500      (-1x SPY)
    "PSQ",  # ProShares Short QQQ          (-1x QQQ)
    "DOG",  # ProShares Short Dow 30       (-1x DJIA)
    "RWM",  # ProShares Short Russell 2000 (-1x IWM)
    "TBF",  # ProShares Short 20+ Year Treasury (-1x TLT)
]


def get_all_etfs() -> List[str]:
    """Return deduplicated list of all ETF tickers across all exchanges."""
    canadian = (
        ISHARES_CA + VANGUARD_CA + BMO_CA + HORIZONS_CA + HAMILTON_CA +
        HARVEST_CA + TD_CA + EVOLVE_CA + PURPOSE_CA + MACKENZIE_CA +
        CI_CA + FIDELITY_CA + MANULIFE_CA
    )
    american = (
        BROAD_US + NASDAQ + INTL_DEVELOPED + EMERGING_MARKETS + GLOBAL +
        SECTOR_SPDR + SECTOR_VANGUARD + SECTOR_SPECIFIC + THEMATIC +
        FIXED_INCOME + COMMODITIES + DIVIDEND + FACTOR + SIZE
        # INVERSE excluded: single-inverse ETFs get selected at the PEAK of
        # bear markets (highest momentum), then held through early recovery
        # when they lose value fastest. Net effect: -2% CAGR drag on Top-5.
    )
    seen, result = set(), []
    for t in canadian + american:
        if t not in seen:
            seen.add(t)
            result.append(t)
    return result


def is_canadian(ticker: str) -> bool:
    return ticker.endswith(".TO") or ticker.endswith(".V") or ticker.endswith(".NE")
