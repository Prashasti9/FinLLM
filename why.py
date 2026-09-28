def money(x):
    return f"${x:,.2f}"


def why_bullets(flagged, baseline, usual):
    """Exact, computed reasons a customer's flagged transactions are unusual."""
    total = len(flagged)

    def count(code):
        return sum(code in reasons for reasons in flagged.reasons)

    out = []
    n = count("LARGE_VS_HISTORY")
    if n:
        out.append(f"{n} of {total} flagged transactions were at least 10x the usual amount of "
                   f"{money(usual)} (highest: {flagged.amount_ratio.max():.1f}x).")
    near = count("NEAR_CTR_THRESHOLD") + count("REPEATED_NEAR_CTR_THRESHOLD")
    if near:
        out.append(f"{near} of {total} were cash deposits between $9,000 and $9,999; "
                   f"{count('REPEATED_NEAR_CTR_THRESHOLD')} of these came with 2 or more such deposits within 7 days.")
    n = count("NEW_RECIPIENT") + count("NEW_RECIPIENT_LARGE")
    if n:
        out.append(f"{n} of {total} went to a recipient this customer had never paid before.")
    n = count("HIGH_VELOCITY")
    if n:
        out.append(f"{n} of {total} were part of a burst of 5 or more transactions within one hour "
                   f"(up to {int(flagged.tx_last_hour.max())} in one hour).")
    n = count("NIGHT_ACTIVITY")
    if n:
        out.append(f"{n} of {total} were made before 6am; {int((baseline.hour < 6).sum())} of the "
                   f"customer's {len(baseline)} other transactions were.")
    n = count("DORMANT_REACTIVATION")
    if n:
        out.append(f"{n} of {total} came after a gap of {flagged.days_since_last.max():.0f} days with no activity.")
    n = count("FOREIGN_DESTINATION")
    if n:
        countries = ", ".join(sorted(flagged.loc[flagged.foreign, "country"].unique()))
        out.append(f"{n} of {total} were sent outside the US ({countries}).")
    if flagged.big_out_7d.max() >= 3:
        out.append(f"Up to {int(flagged.big_out_7d.max())} large outgoing payments (3x usual or more) "
                   f"were made within 7 days.")
    n = count("ML_ANOMALY")
    if n:
        ml_only = flagged[[list(r) == ["ML_ANOMALY"] for r in flagged.reasons]]
        line = f"{n} of {total} were rated statistically unusual by the anomaly model"
        if len(ml_only):
            line += (f"; {len(ml_only)} for that reason alone, at {ml_only.amount_ratio.min():.1f}x to "
                     f"{ml_only.amount_ratio.max():.1f}x the usual amount")
        out.append(line + ".")
    return out
