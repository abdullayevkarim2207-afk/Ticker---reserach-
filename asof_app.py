"""Point-in-time FRED/ALFRED audit app for FIN 43900 Lab 17."""

from __future__ import annotations

from datetime import date
from html import escape
from io import StringIO
import math
import subprocess
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import altair as alt
import pandas as pd
import streamlit as st


alt.data_transformers.disable_max_rows()


SERIES_NAMES = {
    "BAA": "Moody's Baa corporate bond yield",
    "FEDFUNDS": "Federal funds rate",
    "DGS10": "10-year Treasury yield",
    "MORTGAGE30US": "30-year mortgage rate",
}
DEFAULT_SERIES = list(SERIES_NAMES)
FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
ALFRED_CSV_URL = "https://alfred.stlouisfed.org/graph/alfredgraph.csv"
CHART_COLORS = [
    "#2563EB",
    "#F59E0B",
    "#10B981",
    "#EF4444",
    "#8B5CF6",
    "#06B6D4",
    "#EC4899",
    "#64748B",
]
PAGE_CSS = """
<style>
    .stApp {
        background:
            linear-gradient(rgba(15,23,42,.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(15,23,42,.025) 1px, transparent 1px),
            #f4f6f8;
        background-size: 28px 28px;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #e9eef5 100%);
        border-right: 1px solid #cbd5e1;
    }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p { color: #0f172a !important; }
    [data-testid="stSidebar"] input { color: #0f172a !important; }
    [data-testid="stSidebar"] [data-baseweb="tag"] * { color: #0f172a !important; }
    .terminal-hero {
        overflow: hidden;
        border: 1px solid #111827;
        border-radius: 8px;
        background: #090d14;
        box-shadow: 0 14px 34px rgba(2, 6, 23, .20);
        margin-bottom: .65rem;
    }
    .terminal-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        padding: .55rem 1rem;
        border-bottom: 1px solid #263244;
        background: #111827;
        color: #94a3b8;
        font: 700 .73rem/1.2 ui-monospace, SFMono-Regular, Menlo, monospace;
        letter-spacing: .09em;
        text-transform: uppercase;
    }
    .terminal-brand { color: #f59e0b; }
    .terminal-status { display: flex; align-items: center; gap: .45rem; color: #cbd5e1; }
    .status-dot {
        width: .48rem; height: .48rem; border-radius: 50%; background: #22c55e;
        box-shadow: 0 0 10px rgba(34,197,94,.85);
    }
    .terminal-main { padding: 1.3rem 1.4rem 1.2rem; }
    .terminal-main h1 {
        margin: 0;
        color: #f8fafc;
        font-size: clamp(2rem, 4vw, 3.15rem);
        letter-spacing: -.045em;
    }
    .terminal-main p { margin: .4rem 0 0; color: #94a3b8; font-size: 1rem; }
    .terminal-key { color: #f59e0b; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
    .market-strip {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
        gap: 1px;
        padding: 1px;
        margin: .7rem 0 1rem;
        border-radius: 8px;
        overflow: hidden;
        background: #334155;
        box-shadow: 0 10px 24px rgba(15,23,42,.10);
    }
    .market-cell { background: #0f172a; padding: .72rem .85rem; min-height: 78px; }
    .market-id {
        display: flex; justify-content: space-between; gap: .6rem;
        color: #f8fafc; font: 700 .78rem/1.2 ui-monospace, SFMono-Regular, Menlo, monospace;
    }
    .market-value { margin-top: .35rem; color: #fff; font-size: 1.22rem; font-weight: 750; }
    .market-date { margin-top: .15rem; color: #64748b; font-size: .7rem; }
    .move-up { color: #34d399; }
    .move-down { color: #fb7185; }
    .move-flat { color: #94a3b8; }
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, .94);
        border: 1px solid #cbd5e1;
        border-top: 3px solid #f59e0b;
        padding: .7rem .85rem;
        border-radius: 7px;
        box-shadow: 0 7px 18px rgba(15, 23, 42, .06);
    }
    [data-testid="stMetric"] * { color: #0f172a !important; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255,255,255,.96);
        border-color: #cbd5e1;
        border-radius: 7px;
        box-shadow: 0 8px 22px rgba(15, 23, 42, .07);
    }
    .series-name {
        font: 800 1rem/1.3 ui-monospace, SFMono-Regular, Menlo, monospace;
        color: #0f172a;
    }
    .series-meta { color: #64748b; font-size: .82rem; margin: .12rem 0 .35rem; }
    div[data-testid="stDataFrame"] { border-radius: 7px; overflow: hidden; }
    .stTabs [data-baseweb="tab-list"] { gap: 1px; background: #cbd5e1; padding: 1px; }
    .stTabs [data-baseweb="tab"] {
        background: #f8fafc;
        border-radius: 0;
        padding: .52rem 1rem;
    }
    .stTabs [aria-selected="true"] { background: #0f172a; }
    .stTabs [data-baseweb="tab"] p { color: #334155 !important; font-weight: 700; }
    .stTabs [aria-selected="true"] p { color: #f59e0b !important; }
</style>
"""


class SeriesDownloadError(RuntimeError):
    """A readable error for one failed series download."""


def _download_csv(url: str) -> str:
    """Download one public CSV and return its text."""
    # macOS and Streamlit's Linux images include curl. It has proved more
    # reliable for the public FRED endpoints than Python's TLS stack on some
    # campus networks. The urllib path keeps the app portable if curl is absent.
    try:
        result = subprocess.run(
            [
                "curl",
                "--fail",
                "--silent",
                "--show-error",
                "--location",
                "--max-time",
                "60",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=65,
            check=False,
        )
    except FileNotFoundError:
        result = None
    except subprocess.TimeoutExpired as exc:
        raise SeriesDownloadError("The FRED download timed out.") from exc

    if result is not None:
        if result.returncode == 0:
            return result.stdout
        message = result.stderr.strip() or "unknown curl error"
        raise SeriesDownloadError(f"The FRED download failed: {message}")

    request = Request(url, headers={"User-Agent": "FIN43900 point-in-time lab"})
    try:
        with urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8-sig")
    except HTTPError as exc:
        raise SeriesDownloadError(f"FRED returned HTTP {exc.code}.") from exc
    except URLError as exc:
        raise SeriesDownloadError(f"Could not reach FRED: {exc.reason}.") from exc
    except TimeoutError as exc:
        raise SeriesDownloadError("The FRED download timed out.") from exc


def parse_fred_csv(csv_text: str, series_id: str) -> pd.Series:
    """Parse either a FRED or ALFRED one-series CSV into dated values."""
    try:
        frame = pd.read_csv(StringIO(csv_text), na_values=["."])
    except Exception as exc:
        raise SeriesDownloadError("The download was not a readable CSV.") from exc

    if "observation_date" not in frame.columns:
        raise SeriesDownloadError("The download did not contain observation_date.")
    value_columns = [column for column in frame.columns if column != "observation_date"]
    if len(value_columns) != 1:
        raise SeriesDownloadError("The download did not contain exactly one value column.")

    dates = pd.to_datetime(frame["observation_date"], errors="coerce")
    values = pd.to_numeric(frame[value_columns[0]], errors="coerce")
    series = pd.Series(values.to_numpy(), index=dates, name=series_id)
    series = series[~series.index.isna()].dropna().sort_index()
    if series.empty:
        raise SeriesDownloadError(f"No numeric observations were found for {series_id}.")
    return series


@st.cache_data(show_spinner=False, ttl=3600)
def download_today(series_id: str) -> pd.Series:
    """Download the series as FRED reports it today."""
    url = f"{FRED_CSV_URL}?{urlencode({'id': series_id})}"
    return parse_fred_csv(_download_csv(url), series_id)


@st.cache_data(show_spinner=False, ttl=3600)
def download_as_known(series_id: str, vintage_date: date) -> pd.Series:
    """Download the series exactly as ALFRED reported it on vintage_date."""
    query = urlencode({"id": series_id, "vintage_date": vintage_date.isoformat()})
    url = f"{ALFRED_CSV_URL}?{query}"
    return parse_fred_csv(_download_csv(url), series_id)


def audit_counts(today: pd.Series, vintage: pd.Series) -> tuple[int, int]:
    """Return counts of later observations and revised same-date observations."""
    last_known_date = vintage.index.max()
    late_count = int((today.index > last_known_date).sum())

    common_dates = today.index.intersection(vintage.index)
    revised_count = sum(
        not math.isclose(
            float(today.loc[measured_date]),
            float(vintage.loc[measured_date]),
            rel_tol=1e-12,
            abs_tol=1e-12,
        )
        for measured_date in common_dates
    )
    return late_count, revised_count


def is_monthly(series: pd.Series) -> bool:
    """Infer a monthly series so measured dates can be displayed naturally."""
    if len(series) < 2:
        return False
    mostly_first_day = sum(timestamp.day == 1 for timestamp in series.index) / len(series) > 0.9
    typical_gap = series.index.to_series().diff().dt.days.dropna().median()
    return bool(mostly_first_day and typical_gap >= 27)


def format_measured_date(timestamp: pd.Timestamp, series: pd.Series) -> str:
    """Show monthly observations as Month YYYY and others as a full date."""
    if is_monthly(series):
        return timestamp.strftime("%B %Y")
    return timestamp.strftime("%Y-%m-%d")


def format_value(value: float) -> str:
    """Use readable rate precision while keeping large whole-number series tidy."""
    if abs(value) >= 1_000 and float(value).is_integer():
        return f"{value:,.0f}"
    return f"{value:,.2f}"


def series_label(series_id: str) -> str:
    """Format the sidebar's ID-and-name labels."""
    return f"{series_id} — {SERIES_NAMES[series_id]}"


def values_from_start(series: pd.Series, start_date: date) -> pd.Series:
    """Return observations on or after the selected chart start date."""
    return series[series.index.date >= start_date]


def normalize_to_100(frame: pd.DataFrame) -> pd.DataFrame:
    """Index each nonempty column to 100 at its first visible observation."""
    normalized = frame.copy()
    for column in normalized:
        nonmissing = normalized[column].dropna()
        if not nonmissing.empty and float(nonmissing.iloc[0]) != 0:
            normalized[column] = normalized[column] / float(nonmissing.iloc[0]) * 100.0
    return normalized


def latest_move(series: pd.Series) -> tuple[float, float]:
    """Return the latest value and its change from the prior observation."""
    latest = float(series.iloc[-1])
    change = latest - float(series.iloc[-2]) if len(series) > 1 else 0.0
    return latest, change


def market_strip_html(loaded: dict[str, dict]) -> str:
    """Build a compact terminal-style tape for all successfully loaded series."""
    cells = []
    for series_id, item in loaded.items():
        latest, change = latest_move(item["today"])
        if change > 0:
            move_class, arrow = "move-up", "▲"
        elif change < 0:
            move_class, arrow = "move-down", "▼"
        else:
            move_class, arrow = "move-flat", "■"
        measured = format_measured_date(item["today"].index[-1], item["today"])
        cells.append(
            '<div class="market-cell">'
            f'<div class="market-id"><span>{escape(series_id)}</span>'
            f'<span class="{move_class}">{arrow} {change:+,.2f}</span></div>'
            f'<div class="market-value">{format_value(latest)}</div>'
            f'<div class="market-date">LATEST · {escape(measured)}</div>'
            "</div>"
        )
    return '<div class="market-strip">' + "".join(cells) + "</div>"


def terminal_chart_style(chart: alt.Chart) -> alt.Chart:
    """Apply a high-contrast finance-terminal treatment to an Altair chart."""
    return (
        chart.configure(background="#0b1220")
        .configure_view(stroke=None)
        .configure_axis(
            gridColor="#243044",
            gridOpacity=0.75,
            domainColor="#475569",
            tickColor="#475569",
            labelColor="#cbd5e1",
            titleColor="#e2e8f0",
        )
        .configure_legend(
            labelColor="#e2e8f0",
            titleColor="#e2e8f0",
            padding=8,
        )
    )


def main() -> None:
    st.set_page_config(page_title="Point-in-Time Rate Audit", layout="wide")
    st.markdown(PAGE_CSS, unsafe_allow_html=True)

    st.sidebar.header("Audit controls")
    selected = st.sidebar.multiselect(
        "Rate series",
        options=DEFAULT_SERIES,
        default=DEFAULT_SERIES,
        format_func=series_label,
    )
    extra_text = st.sidebar.text_input(
        "Add FRED series IDs",
        placeholder="Example: DGS2, SOFR, PAYEMS",
        help="Enter one ID or several IDs separated by commas.",
    )
    start_date = st.sidebar.date_input("Chart start date", value=date(2020, 1, 1))
    as_known_on = st.sidebar.date_input("As known on", value=date.today())
    st.sidebar.divider()
    chart_layout = st.sidebar.radio(
        "Chart layout",
        options=["Separate charts", "Combined chart"],
        help="Switch between individual cards and one chart containing every selected series.",
    )
    combined_scale = st.sidebar.radio(
        "Combined-chart scale",
        options=["Original values", "Index each series to 100"],
        disabled=chart_layout != "Combined chart",
        help="Indexing makes differently scaled series comparable by setting each first visible value to 100.",
    )

    st.markdown(
        """
        <div class="terminal-hero">
            <div class="terminal-bar">
                <span class="terminal-brand">PIT // RATES MONITOR</span>
                <span class="terminal-status"><span class="status-dot"></span>FRED + ALFRED CONNECTED</span>
            </div>
            <div class="terminal-main">
                <h1>Point-in-Time Audit</h1>
                <p><span class="terminal-key">AS-OF INTELLIGENCE</span> · See today's history and what was actually knowable at the decision date.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Data from FRED and ALFRED, Federal Reserve Bank of St. Louis, "
        f"downloaded {date.today().isoformat()}; built with AI help, a learning "
        "demonstration, not investment advice."
    )

    series_ids = list(selected)
    extra_ids = [part.strip().upper() for part in extra_text.split(",") if part.strip()]
    for extra_id in extra_ids:
        if extra_id not in series_ids:
            series_ids.append(extra_id)

    if not series_ids:
        st.info("Select a rate series or enter another FRED series ID.")
        return

    rows = []
    loaded: dict[str, dict] = {}
    with st.spinner("Downloading FRED and ALFRED data..."):
        for series_id in series_ids:
            try:
                today = download_today(series_id)
                vintage = download_as_known(series_id, as_known_on)
                late_count, revised_count = audit_counts(today, vintage)

                vintage_last_date = vintage.index.max()
                vintage_last_value = float(vintage.iloc[-1])
                today_last_date = today.index.max()
                loaded[series_id] = {
                    "today": today,
                    "vintage": vintage,
                    "vintage_last_date": vintage_last_date,
                    "vintage_last_value": vintage_last_value,
                    "late_count": late_count,
                    "revised_count": revised_count,
                }
                rows.append(
                    {
                        "Series": f"https://fred.stlouisfed.org/series/{series_id}",
                        f"Last measured as of {as_known_on.isoformat()}": format_measured_date(
                            vintage_last_date, vintage
                        ),
                        "As-of value": format_value(vintage_last_value),
                        "Last measured today": format_measured_date(today_last_date, today),
                        "Today's value": format_value(float(today.iloc[-1])),
                        "Values published later": late_count,
                        "Same-date values revised": revised_count,
                    }
                )
            except Exception as exc:
                st.error(f"{series_id}: {exc}")

    if not loaded:
        st.warning("No selected series could be loaded.")
        return

    st.markdown(market_strip_html(loaded), unsafe_allow_html=True)

    metric_columns = st.columns(4)
    metric_columns[0].metric("Series loaded", len(loaded))
    metric_columns[1].metric("As known on", as_known_on.strftime("%b %d, %Y"))
    metric_columns[2].metric(
        "Published later", sum(item["late_count"] for item in loaded.values())
    )
    metric_columns[3].metric(
        "Revisions found", sum(item["revised_count"] for item in loaded.values())
    )

    charts_tab, audit_tab, guide_tab = st.tabs(
        ["📈 Charts", "🔎 Point-in-time table", "ℹ️ How to read it"]
    )

    with charts_tab:
        if chart_layout == "Combined chart":
            combined = pd.concat(
                {
                    series_id: values_from_start(item["today"], start_date)
                    for series_id, item in loaded.items()
                },
                axis=1,
            )
            combined = combined.dropna(how="all")
            if combined.empty:
                st.warning(f"The selected series have no observations on or after {start_date}.")
            else:
                y_label = "Value"
                if combined_scale == "Index each series to 100":
                    combined = normalize_to_100(combined)
                    y_label = "Index (first visible value = 100)"
                with st.container(border=True):
                    st.markdown('<div class="series-name">All selected series</div>', unsafe_allow_html=True)
                    st.markdown(
                        '<div class="series-meta">Hover anywhere on the plot to see the date '
                        "and value on every colored line. Change the scale in the sidebar.</div>",
                        unsafe_allow_html=True,
                    )
                    colors = [
                        CHART_COLORS[index % len(CHART_COLORS)]
                        for index in range(len(combined.columns))
                    ]
                    date_column = combined.index.name or "observation_date"
                    chart_frame = (
                        combined.rename_axis(date_column)
                        .reset_index()
                        .melt(
                            id_vars=date_column,
                            var_name="Series",
                            value_name="Value",
                        )
                        .dropna(subset=["Value"])
                    )
                    # Altair connects lower-frequency observations with straight
                    # segments. Time interpolation makes the crosshair tooltip
                    # report the value at that same position on each visible line
                    # instead of displaying a missing observation as zero.
                    tooltip_frame = (
                        combined.interpolate(method="time", limit_area="inside")
                        .rename_axis(date_column)
                        .reset_index()
                    )
                    hover = alt.selection_point(
                        fields=[date_column],
                        nearest=True,
                        on="pointerover",
                        empty=False,
                        clear="pointerout",
                    )
                    chart_base = alt.Chart(chart_frame).encode(
                        x=alt.X(f"{date_column}:T", title="Measurement date"),
                        y=alt.Y("Value:Q", title=y_label, scale=alt.Scale(zero=False)),
                        color=alt.Color(
                            "Series:N",
                            title=None,
                            scale=alt.Scale(
                                domain=list(combined.columns),
                                range=colors,
                            ),
                            legend=alt.Legend(
                                orient="top",
                                direction="horizontal",
                                columns=2,
                                symbolStrokeWidth=4,
                            ),
                        ),
                        tooltip=[
                            alt.Tooltip("Series:N", title="Series"),
                            alt.Tooltip(
                                f"{date_column}:T",
                                title="Measurement date",
                                format="%b %d, %Y",
                            ),
                            alt.Tooltip("Value:Q", title="Value", format=",.2f"),
                        ],
                    )
                    lines = chart_base.mark_line(strokeWidth=2.4)
                    hover_points = chart_base.mark_point(filled=True, size=72).encode(
                        opacity=alt.condition(hover, alt.value(1), alt.value(0)),
                        tooltip=[
                            alt.Tooltip("Series:N", title="Series"),
                            alt.Tooltip(
                                f"{date_column}:T",
                                title="Measurement date",
                                format="%b %d, %Y",
                            ),
                            alt.Tooltip("Value:Q", title="Value", format=",.2f"),
                        ],
                    )
                    selectors = (
                        alt.Chart(tooltip_frame)
                        .mark_point(opacity=0)
                        .encode(
                            x=alt.X(f"{date_column}:T"),
                            tooltip=[
                                alt.Tooltip(
                                    f"{date_column}:T",
                                    title="Measurement date",
                                    format="%b %d, %Y",
                                ),
                                *[
                                    alt.Tooltip(
                                        f"{series_id}:Q",
                                        title=series_id,
                                        format=",.2f",
                                    )
                                    for series_id in combined.columns
                                ],
                            ],
                        )
                        .add_params(hover)
                    )
                    hover_rule = (
                        alt.Chart(tooltip_frame)
                        .mark_rule(color="#94a3b8", strokeDash=[4, 4])
                        .encode(
                            x=alt.X(f"{date_column}:T"),
                            opacity=alt.condition(hover, alt.value(0.85), alt.value(0)),
                            tooltip=[
                                alt.Tooltip(
                                    f"{date_column}:T",
                                    title="Measurement date",
                                    format="%b %d, %Y",
                                ),
                                *[
                                    alt.Tooltip(f"{series_id}:Q", title=series_id, format=",.2f")
                                    for series_id in combined.columns
                                ],
                            ],
                        )
                    )
                    combined_chart = terminal_chart_style(
                        alt.layer(lines, hover_points, selectors, hover_rule)
                        .properties(height=500)
                        .interactive(bind_y=False)
                    )
                    st.altair_chart(combined_chart, use_container_width=True)
        else:
            chart_columns = st.columns(2)
            for index, (series_id, item) in enumerate(loaded.items()):
                with chart_columns[index % 2]:
                    with st.container(border=True):
                        st.markdown(
                            f'<div class="series-name">{series_id} · '
                            f"{SERIES_NAMES.get(series_id, 'FRED series')}</div>",
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f'<div class="series-meta">Last known on {as_known_on.isoformat()}: '
                            f"{format_measured_date(item['vintage_last_date'], item['vintage'])} · "
                            f"{format_value(item['vintage_last_value'])}</div>",
                            unsafe_allow_html=True,
                        )
                        chart_data = values_from_start(item["today"], start_date)
                        if chart_data.empty:
                            st.warning(f"No observations on or after {start_date}.")
                        else:
                            date_column = chart_data.index.name or "observation_date"
                            chart_frame = (
                                chart_data.rename("Value")
                                .rename_axis(date_column)
                                .reset_index()
                            )
                            hover = alt.selection_point(
                                fields=[date_column],
                                nearest=True,
                                on="pointerover",
                                empty=False,
                                clear="pointerout",
                            )
                            chart_base = alt.Chart(chart_frame).encode(
                                x=alt.X(
                                    f"{date_column}:T",
                                    title="Measurement date",
                                ),
                                y=alt.Y(
                                    "Value:Q",
                                    title="Value",
                                    scale=alt.Scale(zero=False),
                                ),
                                tooltip=[
                                    alt.Tooltip(
                                        f"{date_column}:T",
                                        title="Measurement date",
                                        format="%b %d, %Y",
                                    ),
                                    alt.Tooltip(
                                        "Value:Q",
                                        title=series_id,
                                        format=",.2f",
                                    ),
                                ],
                            )
                            line = chart_base.mark_line(
                                color=CHART_COLORS[index % len(CHART_COLORS)],
                                strokeWidth=2.2,
                            )
                            hover_point = chart_base.mark_point(
                                color=CHART_COLORS[index % len(CHART_COLORS)],
                                filled=True,
                                size=80,
                            ).encode(
                                opacity=alt.condition(hover, alt.value(1), alt.value(0)),
                            )
                            selector = (
                                alt.Chart(chart_frame)
                                .mark_point(opacity=0)
                                .encode(
                                    x=alt.X(f"{date_column}:T"),
                                    tooltip=[
                                        alt.Tooltip(
                                            f"{date_column}:T",
                                            title="Measurement date",
                                            format="%b %d, %Y",
                                        ),
                                        alt.Tooltip(
                                            "Value:Q",
                                            title=series_id,
                                            format=",.2f",
                                        ),
                                    ],
                                )
                                .add_params(hover)
                            )
                            hover_rule = (
                                alt.Chart(chart_frame)
                                .mark_rule(color="#94a3b8", strokeDash=[4, 4])
                                .encode(
                                    x=alt.X(f"{date_column}:T"),
                                    opacity=alt.condition(
                                        hover,
                                        alt.value(0.85),
                                        alt.value(0),
                                    ),
                                    tooltip=[
                                        alt.Tooltip(
                                            f"{date_column}:T",
                                            title="Measurement date",
                                            format="%b %d, %Y",
                                        ),
                                        alt.Tooltip(
                                            "Value:Q",
                                            title=series_id,
                                            format=",.2f",
                                        ),
                                    ],
                                )
                            )
                            single_chart = terminal_chart_style(
                                alt.layer(line, hover_point, selector, hover_rule)
                                .properties(height=260)
                                .interactive(bind_y=False)
                            )
                            st.altair_chart(single_chart, use_container_width=True)

    with audit_tab:
        st.subheader("What was known then versus what the file says today")
        st.dataframe(
            pd.DataFrame(rows),
            hide_index=True,
            use_container_width=True,
            column_config={
                "Series": st.column_config.LinkColumn(
                    "Series",
                    display_text=r"https://fred\.stlouisfed\.org/series/(.*)",
                )
            },
        )
        st.caption(
            "Values published later counts today's nonmissing observations after the last "
            "measurement available on the selected date. Revisions compare numeric values "
            "only where both downloads contain the same measurement date."
        )

    with guide_tab:
        st.subheader("A quick reading guide")
        st.markdown(
            """
            - **As known on** recreates the ALFRED vintage that existed on your chosen decision date.
            - **Published later** identifies observations that a trader could not yet have seen.
            - **Same-date values revised** identifies historical numbers that changed afterward.
            - **Separate charts** are best for reading exact movements in each series.
            - **Combined chart** compares their paths; use **Index each series to 100** when units or scales differ.
            """
        )


if __name__ == "__main__":
    main()
