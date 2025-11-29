from pathlib import Path

import pandas as pd
import yaml
from clickhouse_driver import Client


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config_example.yaml"


def load_config(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_clickhouse_client(cfg: dict) -> Client:
    ch_cfg = cfg["clickhouse"]

    client = Client(
        host=ch_cfg.get("host", "localhost"),
        port=ch_cfg.get("port", 9000),
        user="default",      # фиксируем пользователя явно
        password="",         # по умолчанию без пароля
        database=ch_cfg.get("database", "default"),
        secure=ch_cfg.get("secure", False),
    )
    return client



def create_schema_if_needed(client: Client):
    sql_path = BASE_DIR / "sql" / "create_tables.sql"
    with open(sql_path, "r", encoding="utf-8") as f:
        sql_text = f.read()

    # ClickHouse клиенту лучше отправлять стейтменты по одному
    for stmt in sql_text.split(";"):
        stmt = stmt.strip()
        if stmt:
            client.execute(stmt)


def prepare_dataframe(cfg: dict) -> pd.DataFrame:
    data_cfg = cfg["data"]
    csv_path = BASE_DIR / data_cfg["path"]

    df = pd.read_csv(csv_path)

    # Приводим названия колонок к нижнему регистру
    df.columns = [c.strip().lower() for c in df.columns]

    # Ожидаем колонки:
    # store, date, weekly_sales, holiday_flag, temperature, fuel_price, cpi, unemployment

    df["week_date"] = pd.to_datetime(
        df["date"],
        format=data_cfg.get("date_format", "%d-%m-%Y"),
        dayfirst=True,
    ).dt.date

    df = df[
        [
            "store",
            "week_date",
            "weekly_sales",
            "holiday_flag",
            "temperature",
            "fuel_price",
            "cpi",
            "unemployment",
        ]
    ]

    return df


def load_to_clickhouse():
    cfg = load_config(CONFIG_PATH)
    client = get_clickhouse_client(cfg)

    create_schema_if_needed(client)
    df = prepare_dataframe(cfg)

    records = [
        (
            int(row["store"]),
            row["week_date"],
            float(row["weekly_sales"]),
            int(row["holiday_flag"]),
            float(row["temperature"]),
            float(row["fuel_price"]),
            float(row["cpi"]),
            float(row["unemployment"]),
        )
        for _, row in df.iterrows()
    ]

    client.execute(
        """
        INSERT INTO walmart.weekly_sales
        (store, week_date, weekly_sales, holiday_flag,
         temperature, fuel_price, cpi, unemployment)
        VALUES
        """,
        records,
    )

    print(f"Загружено строк: {len(records)}")


if __name__ == "__main__":
    load_to_clickhouse()
