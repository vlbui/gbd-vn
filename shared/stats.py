"""Statistical indicators for transition analysis.

Functions follow published conventions (GBD, WHO SDG, Clegg 2009 joinpoint
AAPC). See inline citations on each function.
"""

import numpy as np
import pandas as pd
from scipy import stats

try:
    import ruptures as rpt
    _HAS_RUPTURES = True
except Exception:
    _HAS_RUPTURES = False

from .constants import CAUSE_GROUPS, CAUSE_SHORT, MEASURE, AGE_BANDS_30_69


def calculate_aapc(years, rates):
    """Single-segment log-linear AAPC with 95% CI and p-value.

    Assumes constant annual percent change over the period. For piecewise
    slopes use `joinpoint_aapc`.
    """
    years = np.asarray(years, dtype=float)
    rates = np.asarray(rates, dtype=float)
    mask = ~np.isnan(rates) & ~np.isinf(rates) & (rates > 0)
    y = years[mask]
    r = rates[mask]
    if len(y) < 3:
        return dict(aapc=np.nan, ci_low=np.nan, ci_high=np.nan, p_value=np.nan,
                    n_obs=len(y))
    slope, intercept, _, p, se = stats.linregress(y, np.log(r))
    aapc = (np.exp(slope) - 1) * 100
    ci_low = (np.exp(slope - 1.96 * se) - 1) * 100
    ci_hi = (np.exp(slope + 1.96 * se) - 1) * 100
    return dict(aapc=aapc, ci_low=ci_low, ci_high=ci_hi, p_value=p,
                n_obs=int(len(y)))


def cause_shares(df_level1, country=None):
    """Percent-of-total DALY composition by cause group.

    Uses Both-sex age-standardized DALY rate per 100k as the composition
    substrate (scale-invariant for shares). Returns a wide DataFrame
    indexed by (location_name, year) with CMNN/NCD/Injuries absolute rates,
    their share_pct columns, and cmnn_ncd_ratio.

    Reference: IHME GBD Results Tool; Murray et al. 2020.
    """
    df = df_level1
    if country is not None:
        df = df[df["location_name"] == country]
    cmnn = CAUSE_GROUPS["cmnn"]
    ncd = CAUSE_GROUPS["ncd"]
    inj = CAUSE_GROUPS["injuries"]
    sub = df[(df["measure_name"] == MEASURE["daly"])
             & (df["metric_name"] == "Rate")
             & (df["age_name"] == "Age-standardized")
             & (df["sex_name"] == "Both")
             & (df["cause_name"].isin([cmnn, ncd, inj]))]
    wide = (sub.assign(short=sub["cause_name"].map(CAUSE_SHORT))
            .pivot_table(index=["location_name", "year"],
                         columns="short", values="val"))
    for c in ("CMNN", "NCD", "Injuries"):
        if c not in wide.columns:
            wide[c] = np.nan
    total = wide[["CMNN", "NCD", "Injuries"]].sum(axis=1)
    wide["cmnn_share_pct"] = wide["CMNN"] / total * 100
    wide["ncd_share_pct"] = wide["NCD"] / total * 100
    wide["injuries_share_pct"] = wide["Injuries"] / total * 100
    wide["cmnn_ncd_ratio"] = wide["CMNN"] / wide["NCD"]
    return wide.reset_index()


def probability_30q70(deaths, population):
    """Unconditional probability of dying between ages 30 and 70.

    WHO/GBD life-table formulation, actuarial 5-year intervals:
        q_{30,70} = 1 - prod_{x in {30,35,...,65}} (1 - 5 m_x / (1 + 2.5 m_x))

    Refs: WHO Global Action Plan for NCDs 2013-2020; UN SDG 3.4.1.

    Inputs are length-8 arrays matching AGE_BANDS_30_69. `deaths` are
    numbers, not rates. Returns float in [0,1] or NaN on bad input.
    """
    d = np.asarray(deaths, dtype=float)
    p = np.asarray(population, dtype=float)
    if d.shape != p.shape or d.size != 8:
        raise ValueError(f"expected 8 age bands; got d={d.shape}, p={p.shape}")
    if np.any(np.isnan(d)) or np.any(np.isnan(p)) or np.any(p <= 0):
        return np.nan
    m = d / p
    q5 = 5 * m / (1 + 2.5 * m)
    return float(1 - np.prod(1 - q5))


def joinpoint_aapc(years, y, max_joins=3, max_bkps=None):
    """Joinpoint (piecewise log-linear) AAPC with 95% CI via the delta method.

    Uses `ruptures.Dynp` with l2 cost on detrended log(y) to locate up to
    `max_joins` breakpoints; selects best k (0..max_joins) by BIC. Each
    segment refit as simple log-linear regression with pooled residual
    variance. AAPC = weighted (by segment-year span) mean of segment
    log-slopes; 95% CI via delta method assuming segments approximately
    independent.

    Refs:
      Kim HJ et al. Stat Med 2000;19:335-51.
      Clegg LX et al. Stat Med 2009;28:3670-82.

    Returns dict: aapc, ci_low, ci_high (%), p_value, n_obs, bkps_k, segments.
    """
    if max_bkps is not None:  # legacy name
        max_joins = max_bkps
    years = np.asarray(years, dtype=float)
    y = np.asarray(y, dtype=float)
    order = np.argsort(years)
    years, y = years[order], y[order]
    mask = (y > 0) & ~np.isnan(y)
    years, y = years[mask], y[mask]
    n = len(years)
    if n < 4:
        return dict(aapc=np.nan, ci_low=np.nan, ci_high=np.nan,
                    p_value=np.nan, n_obs=int(n),
                    bkps_k=0, segments=[])
    log_y = np.log(y)

    def _fit_segments(bkps):
        """Per-segment log-linear regression with pooled residual variance
        (Clegg 2009): s² = RSS_total / (n - 2*num_segments)."""
        segs_xy = []
        ssr = 0.0
        prev = 0
        for b in bkps:
            xs = years[prev:b]
            ys = log_y[prev:b]
            if len(xs) < 2:
                prev = b
                continue
            X = np.vstack([xs, np.ones_like(xs)]).T
            beta, *_ = np.linalg.lstsq(X, ys, rcond=None)
            resid = ys - X @ beta
            ssr += float((resid ** 2).sum())
            segs_xy.append((xs, ys, beta, X))
            prev = b

        num_seg = len(segs_xy)
        dof_total = n - 2 * num_seg
        s2 = (ssr / dof_total) if dof_total > 0 else float("nan")

        segs = []
        for xs, ys, beta, X in segs_xy:
            if not np.isnan(s2):
                cov = np.linalg.inv(X.T @ X) * s2
                slope_se = float(np.sqrt(cov[0, 0]))
            else:
                slope_se = float("nan")
            segs.append({
                "start_year": int(xs[0]), "end_year": int(xs[-1]),
                "n_years": int(len(xs)),
                "slope": float(beta[0]), "slope_se": slope_se,
                "apc_pct": float((np.exp(beta[0]) - 1) * 100),
            })
        return segs, ssr

    # Linear detrend so change-point detection targets slope changes.
    X_full = np.vstack([years, np.ones_like(years)]).T
    beta_full, *_ = np.linalg.lstsq(X_full, log_y, rcond=None)
    resid_full = log_y - X_full @ beta_full

    best = None
    for k in range(0, max_joins + 1):
        if (k + 1) * 2 > n:
            continue
        if k == 0 or not _HAS_RUPTURES:
            bkps = [n]
        else:
            try:
                algo = rpt.Dynp(model="l2", min_size=2, jump=1).fit(resid_full)
                bkps = algo.predict(n_bkps=k)
            except Exception:
                bkps = [n]
        segs, ssr = _fit_segments(bkps)
        if not segs:
            continue
        p = 2 * len(segs) + k  # 2 per segment + k breakpoint positions
        bic = n * np.log(max(ssr / n, 1e-12)) + p * np.log(n)
        if best is None or bic < best["bic"]:
            best = dict(bic=bic, segs=segs, k=k)

    segs = best["segs"]
    w = np.array([max(s["n_years"] - 1, 1) for s in segs], dtype=float)
    w_tot = w.sum()
    if w_tot <= 0 or any(np.isnan(s["slope_se"]) for s in segs):
        aapc = (np.exp(segs[0]["slope"]) - 1) * 100 if segs else np.nan
        return dict(aapc=aapc, ci_low=np.nan, ci_high=np.nan,
                    p_value=np.nan, n_obs=int(n),
                    bkps_k=best["k"], segments=segs)
    weighted_slope = float(np.sum([w[i] * segs[i]["slope"]
                                   for i in range(len(segs))]) / w_tot)
    var_slope = float(np.sum([(w[i] / w_tot) ** 2 * segs[i]["slope_se"] ** 2
                              for i in range(len(segs))]))
    se = float(np.sqrt(var_slope))
    aapc = (np.exp(weighted_slope) - 1) * 100
    ci_low = (np.exp(weighted_slope - 1.96 * se) - 1) * 100
    ci_high = (np.exp(weighted_slope + 1.96 * se) - 1) * 100
    if se > 0:
        z = weighted_slope / se
        p_value = float(2 * (1 - stats.norm.cdf(abs(z))))
    else:
        p_value = float("nan")
    return dict(aapc=aapc, ci_low=ci_low, ci_high=ci_high,
                p_value=p_value, n_obs=int(n),
                bkps_k=best["k"], segments=segs)


# Back-compat alias for earlier drafts that imported the CI variant.
joinpoint_aapc_ci = joinpoint_aapc


def joinpoint_aapc_pelt(years, values, max_joins=3):
    """Joinpoint AAPC using `ruptures.Pelt(model='l2')` with BIC-style
    penalty `pen = 2*log(n)`, capped at `max_joins` breakpoints.

    Faster than Dynp; used by the SDG 3.4.1 30q70 pipeline. Aggregation
    follows Clegg 2009 (weighted mean of segment log-slopes; CI via
    quadrature of segment SEs with pooled residual variance).

    Returns dict: aapc, ci_low, ci_high, n_bkps, segments.
    """
    years = np.asarray(years, dtype=float)
    values = np.asarray(values, dtype=float)
    order = np.argsort(years)
    years, values = years[order], values[order]
    mask = (values > 0) & ~np.isnan(values)
    years, values = years[mask], values[mask]
    n = len(years)
    if n < 4:
        return dict(aapc=np.nan, ci_low=np.nan, ci_high=np.nan,
                    n_bkps=0, segments=[])

    log_y = np.log(values)

    if _HAS_RUPTURES:
        try:
            algo = rpt.Pelt(model="l2", min_size=2, jump=1).fit(log_y)
            raw = algo.predict(pen=2 * np.log(n))
            cuts = [c for c in raw if 0 < c < n][:max_joins]
            bkps = cuts + [n]
        except Exception:
            bkps = [n]
    else:
        bkps = [n]

    segs_xy = []
    ssr = 0.0
    prev = 0
    for b in bkps:
        xs = years[prev:b]
        ys = log_y[prev:b]
        if len(xs) >= 2:
            X = np.vstack([xs, np.ones_like(xs)]).T
            beta, *_ = np.linalg.lstsq(X, ys, rcond=None)
            resid = ys - X @ beta
            ssr += float((resid ** 2).sum())
            segs_xy.append((xs, ys, beta, X))
        prev = b

    num_seg = len(segs_xy)
    if num_seg == 0:
        return dict(aapc=np.nan, ci_low=np.nan, ci_high=np.nan,
                    n_bkps=0, segments=[])
    dof = n - 2 * num_seg
    s2 = (ssr / dof) if dof > 0 else float("nan")

    segs = []
    for xs, _ys, beta, X in segs_xy:
        slope_se = float("nan")
        if not np.isnan(s2):
            cov = np.linalg.inv(X.T @ X) * s2
            slope_se = float(np.sqrt(cov[0, 0]))
        segs.append(dict(start=int(xs[0]), end=int(xs[-1]),
                         n_years=int(len(xs)),
                         slope=float(beta[0]), slope_se=slope_se,
                         apc_pct=float((np.exp(beta[0]) - 1) * 100)))

    w = np.array([max(s["n_years"] - 1, 1) for s in segs], dtype=float)
    w_tot = w.sum()
    if w_tot <= 0 or any(np.isnan(s["slope_se"]) for s in segs):
        return dict(aapc=(np.exp(segs[0]["slope"]) - 1) * 100,
                    ci_low=np.nan, ci_high=np.nan,
                    n_bkps=max(0, num_seg - 1), segments=segs)

    weighted_slope = float(sum(w[i] * segs[i]["slope"]
                               for i in range(num_seg)) / w_tot)
    var_slope = float(sum((w[i] / w_tot) ** 2 * segs[i]["slope_se"] ** 2
                          for i in range(num_seg)))
    se = float(np.sqrt(var_slope))
    aapc = (np.exp(weighted_slope) - 1) * 100
    ci_low = (np.exp(weighted_slope - 1.96 * se) - 1) * 100
    ci_high = (np.exp(weighted_slope + 1.96 * se) - 1) * 100
    return dict(aapc=aapc, ci_low=ci_low, ci_high=ci_high,
                n_bkps=max(0, num_seg - 1), segments=segs)
