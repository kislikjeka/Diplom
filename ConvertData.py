import os
import datetime
import pandas as pd

dirPath = "../Original Data"
if os.path.exists(dirPath):
    data_sets = os.listdir(dirPath)
else:
    data_sets = []

common = pd.DataFrame()
for dataset in data_sets:
    df = (
        pd.read_csv(dirPath + "/" + dataset)
            .drop(columns=["_id"])
            .dropna(subset=["Количество мест 15/06/2019", "Количество мест 16/06/2019"])
    )
    df["morning"] = df["Время выезда "].apply(
        lambda x: 1
        if (
                datetime.time(9, 0) > pd.to_datetime(x).time() > datetime.time(5, 0)
        )
        else 0
    )
    df["day"] = df["Время выезда "].apply(
        lambda x: 1
        if (
                datetime.time(14, 0) > pd.to_datetime(x).time() > datetime.time(9, 0)
        )
        else 0
    )
    df["evening"] = df["Время выезда "].apply(
        lambda x: 1
        if (
                datetime.time(18, 0) > pd.to_datetime(x).time() > datetime.time(14, 0)
        )
        else 0
    )
    df["night"] = df["Время выезда "].apply(
        lambda x: 1
        if (
                datetime.time(23, 59) > pd.to_datetime(x).time() > datetime.time(18, 0)
        )
        else 0
    )
    df["econ"] = df["Класс вагона"].apply(lambda x: 1 if (x in ["2Р", "2С"]) else 0)
    df["econ_plus"] = df["Класс вагона"].apply(lambda x: 1 if (x in ["2В"]) else 0)
    df["bistro"] = df["Класс вагона"].apply(lambda x: 1 if (x in ["2Е"]) else 0)
    df["business"] = df["Класс вагона"].apply(lambda x: 1 if (x in ["1С"]) else 0)
    df["first_class"] = df["Класс вагона"].apply(lambda x: 1 if (x in ["1В"]) else 0)
    df["piter_dummy"] = df['Вокзал приезда'].apply(lambda x: 1 if ("Москва" in x) else 0)

    mesta_df = pd.melt(
        df,
        id_vars=[
            "Поезд_вагон",
            "Номер вагона",
            "Номер поезда",
            "Дата выезда",
            "Время выезда ",
            "Вокзал выезда",
            "econ",
            "econ_plus",
            "bistro",
            "business",
            "first_class",
            "morning",
            "day",
            "evening",
            "night",
            "piter_dummy"
        ],
        value_vars=df.columns[df.columns.str.contains("Количество мест")],
        var_name="Date",
        value_name="mesta",
    )
    mesta_df["Date"] = mesta_df["Date"].str.replace("Количество мест", "")

    ceni_df = pd.melt(
        df,
        id_vars=["Поезд_вагон", "Класс вагона", "Номер вагона", "Дата выезда"],
        value_vars=df.columns[df.columns.str.contains("Цена")],
        var_name="Date",
        value_name="ceni",
    )
    ceni_df["Date"] = ceni_df["Date"].str.replace("Цена", "")

    union = pd.merge(ceni_df, mesta_df)
    union["Дата выезда"] = pd.to_datetime(
        union["Дата выезда"].apply(lambda x: x if (len(str(x)) == 8) else "0" + str(x)),
        format="%d%m%Y",
    )

    union["Date"] = pd.to_datetime(union["Date"], format=" %d/%m/%Y")
    union["day_of_week"] = union["Дата выезда"].dt.day_name()
    union["t"] = (union["Дата выезда"].dt.date - union["Date"].dt.date).apply(
        lambda x: x.days
    )
    union["tsquare"] = union["t"] * union["t"]
    union = union.sort_values(["Поезд_вагон", "Date"]).reset_index(drop=True)
    union = union.rename(
        columns={
            "Поезд_вагон": "i",
            "Вокзал выезда": "vokzal",
            "Дата выезда": "dep_date",
        }
    )
    union["mesta_lag"] = union["mesta"].shift(1)
    union["sold_yes"] = union["mesta_lag"] - union["mesta"]
    union["ceni_lag"] = union["ceni"].shift(1)
    union.drop("Date", axis=1)
    union = union.dropna()

    common = common.append(union)

common.to_csv("../Data/dataset.csv")
