# Дашборды сети Walmart

Проект представляет собой аналитическую витрину и дашборды на основе исторических данных продаж Walmart.  
Используется ClickHouse как высокопроизводительное хранилище и Streamlit для визуализации ключевых бизнес-метрик.

---

## Цели проекта

- Построить аналитическую модель на основе исторических данных розничной сети.
- Сформировать аналитические витрины и SQL-запросы для анализа продаж.
- Реализовать интерактивные дашборды (Streamlit), доступные локально.
- Оценить влияние праздничных недель и внешних факторов на продажи.
- Построить рейтинг магазинов по выручке и средним продажам.

---

## Структура проекта
```
walmart-dashboards/
│
├── app.py
├── README.md   
├── requirements.txt
├── config_example.yaml
├── .gitignore 
│
├── data/
│   └── Walmart_Sales.csv 
│
├── images/
│   ├── photo_2025-11-29_21-49-57.jpg
│   ├── photo_2025-11-29_21-50-03.jpg
│   ├── photo_2025-11-29_21-50-07.jpg
│   └── photo_2025-11-29_21-50-10.jpg
│
├── sql/
│   ├── create_tables.sql
│   ├── drop_tables.sql
│   ├── daily_sales.sql
│   ├── holiday_impact.sql 
│   ├── store_ranking.sql
│   └── external_factors.sql 
│
├── etl/
│   └── load_walmart_sales.py
│
└── dashboards/ 
    ├── product_health.md
    ├── holiday_impact.md
    ├── store_ranking.md
    └── external_factors.md

```


---

## Используемый стек

Python, ClickHouse, SQL, Streamlit, WSL, pandas, numpy, matplotlib

---

## Запуск проекта

### 1. Подготовка виртуального окружения

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Запуск ClickHouse

```
sudo service clickhouse-server start
clickhouse-client
```

### 3. Загрузка данных Walmart в ClickHouse

```
python etl/load_walmart_sales.py
```

### 4. Запуск Streamlit-дашборда

```
streamlit run app.py
```

## Дашборды

### 1. Продажи по сети
![Network Sales](images/photo_2025-11-29_21-50-07.jpg)

### 2. Рейтинг магазинов
![Store Ranking](images/photo_2025-11-29_21-50-10.jpg)

### 3. Праздничные недели
![Holiday Impact](images/photo_2025-11-29_21-49-57.jpg)

### 4. Внешние факторы
![External Factors](images/photo_2025-11-29_21-50-03.jpg)
