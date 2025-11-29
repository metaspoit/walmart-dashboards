from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st
import yaml
from clickhouse_driver import Client


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config_example.yaml"




def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@st.cache_resource
def get_clickhouse_client():
    client = Client(
        host="localhost",
        port=9000,
        user="default",      # ВАЖНО: явно default
        password="",
        database="walmart",  # если БД у тебя называется иначе – поменяй
        secure=False,
    )
    return client



@st.cache_data
def get_date_bounds() -> tuple[date, date]:
    client = get_clickhouse_client()
    rows = client.execute(
        "SELECT min(week_date), max(week_date) FROM walmart.weekly_sales"
    )
    if not rows:
        # если таблица вдруг пустая
        raise ValueError("В таблице walmart.weekly_sales нет данных")

    min_date, max_date = rows[0]
    return min_date, max_date



@st.cache_data
def query_to_df(query: str, params: dict | None = None) -> pd.DataFrame:
    client = get_clickhouse_client()
    data, columns = client.execute(query, params or {}, with_column_types=True)
    col_names = [c[0] for c in columns]
    df = pd.DataFrame(data, columns=col_names)
    return df




def page_sales_over_time():
    st.header("Дашборд: динамика продаж по сети")

    min_date, max_date = get_date_bounds()
    start, end = st.sidebar.date_input(
        "Период анализа",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(start, tuple) or isinstance(end, tuple):
        start, end = min_date, max_date

    if start > end:
        st.error("Начальная дата больше конечной.")
        return

    query = """
        SELECT
            week_date,
            sum(weekly_sales) AS weekly_sales_total
        FROM walmart.weekly_sales
        WHERE week_date BETWEEN %(start)s AND %(end)s
        GROUP BY week_date
        ORDER BY week_date
    """

    df = query_to_df(query, {"start": start, "end": end})
    if df.empty:
        st.warning("Нет данных за выбранный период.")
        return

    df = df.sort_values("week_date")
    df = df.set_index("week_date")

    st.line_chart(df["weekly_sales_total"])

    st.subheader("Таблица данных")
    st.dataframe(df)


def page_store_ranking():
    st.header("Дашборд: рейтинг магазинов по продажам")

    query = """
        SELECT
            store,
            avg(weekly_sales) AS avg_weekly_sales,
            sum(weekly_sales) AS total_sales
        FROM walmart.weekly_sales
        GROUP BY store
        ORDER BY avg_weekly_sales DESC
        LIMIT 50
    """

    df = query_to_df(query)
    if df.empty:
        st.warning("Нет данных.")
        return

    st.subheader("Бар-чарт по средним продажам (Top 20)")
    top = df.sort_values("avg_weekly_sales", ascending=False).head(20)
    st.bar_chart(
        data=top.set_index("store")["avg_weekly_sales"],
    )

    st.subheader("Таблица рейтинга магазинов")
    st.dataframe(df)


def page_holiday_impact():
    st.header("Дашборд: влияние праздничных недель на продажи")

    query = """
        SELECT
            store,
            holiday_flag,
            avg(weekly_sales) AS avg_weekly_sales
        FROM walmart.weekly_sales
        GROUP BY store, holiday_flag
        ORDER BY store, holiday_flag
    """

    df = query_to_df(query)
    if df.empty:
        st.warning("Нет данных.")
        return

    pivot = df.pivot(index="store", columns="holiday_flag", values="avg_weekly_sales")
    pivot = pivot.fillna(0)

    st.subheader("Сравнение средних продаж (праздник vs обычные недели)")

    cols_rename = {}
    if 0 in pivot.columns:
        cols_rename[0] = "Обычные недели"
    if 1 in pivot.columns:
        cols_rename[1] = "Праздничные недели"
    pivot = pivot.rename(columns=cols_rename)

    st.bar_chart(pivot)


def page_external_factors():
    st.header("Дашборд: влияние внешних факторов")

    min_date, max_date = get_date_bounds()
    start, end = st.sidebar.date_input(
        "Период анализа (внешние факторы)",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(start, tuple) or isinstance(end, tuple):
        start, end = min_date, max_date

    if start > end:
        st.error("Начальная дата больше конечной.")
        return

    query = """
        SELECT
            week_date,
            sum(weekly_sales)                    AS weekly_sales_total,
            avg(temperature)                     AS avg_temperature,
            avg(fuel_price)                      AS avg_fuel_price,
            avg(cpi)                             AS avg_cpi,
            avg(unemployment)                    AS avg_unemployment
        FROM walmart.weekly_sales
        WHERE week_date BETWEEN %(start)s AND %(end)s
        GROUP BY week_date
        ORDER BY week_date
    """

    df = query_to_df(query, {"start": start, "end": end})
    if df.empty:
        st.warning("Нет данных за выбранный период.")
        return

    df = df.sort_values("week_date").set_index("week_date")

    st.subheader("Продажи по сети")
    st.line_chart(df["weekly_sales_total"])

    st.subheader("Внешние факторы")
    st.line_chart(df[["avg_temperature", "avg_fuel_price", "avg_cpi", "avg_unemployment"]])

    st.subheader("Таблица данных")
    st.dataframe(df)




def main():
    st.set_page_config(page_title="Walmart Analytics", layout="wide")

    st.sidebar.title("Навигация")
    page = st.sidebar.radio(
        "Выберите дашборд",
        (
            "Продажи по сети",
            "Рейтинг магазинов",
            "Праздничные недели",
            "Внешние факторы",
        ),
    )

    if page == "Продажи по сети":
        page_sales_over_time()
    elif page == "Рейтинг магазинов":
        page_store_ranking()
    elif page == "Праздничные недели":
        page_holiday_impact()
    elif page == "Внешние факторы":
        page_external_factors()


if __name__ == "__main__":
    main()
