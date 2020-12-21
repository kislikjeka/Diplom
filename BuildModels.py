from sklearn import metrics
import pandas as pd
import numpy as np
import pickle

from scipy import stats as SS
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt

pd.options.mode.chained_assignment = None

types = ['econ', 'econ_plus', 'business', 'bistro', 'first_class']
dataDir = "../Data"
model_dir = "../Models/"
df = pd.read_csv(dataDir + "/dataset.csv")

stat_df = pd.DataFrame(columns=['Model', "CI (95%)", 'R2', 'MAE'])

for car_type in types:
    # Фильтрация выбросов
    type_df = df[df[car_type] == 1].copy()
    Q1 = type_df['ceni'].quantile(0.25)
    Q3 = type_df['ceni'].quantile(0.75)
    IQR = Q3 - Q1
    lower_range = Q1 - (1.5 * IQR)
    upper_range = Q3 + (1.5 * IQR)
    type_df = type_df[type_df['ceni'] > lower_range]
    type_df = type_df[type_df['ceni'] < upper_range]

    type_df['FE'] = type_df["i"] + type_df["day_of_week"]
    x_train = type_df.loc[:, ("FE", "t", "tsquare", "day", "morning",
                              "evening", "night", "piter_dummy", "ceni_lag")]
    x_train = pd.get_dummies(x_train, columns=["FE"])
    y_label = type_df.loc[:, "ceni"]

    X_train, X_test, y_train, y_test = train_test_split(x_train, y_label, test_size=0.2, random_state=42)

    print("X_train: {}, X_test: {}, y_train: {}, y_test: {}".format(len(X_train.index), len(X_test.index),
                                                                    len(y_train.index), len(y_test.index)))

    orig_model = LinearRegression().fit(x_train, y_label)
    orig_R2 = orig_model.score(x_train, y_label)
    print("Orig R2 for model {}: {}".format(car_type, orig_R2))

    predictions = orig_model.predict(x_train)
    MAE = metrics.mean_absolute_error(y_label, predictions)
    print("Orig MAE for model {}: {}".format(car_type, MAE))

    stdev = np.sqrt(sum((predictions - y_label) ** 2) / (len(y_label) - 2))
    print("CI for model {}: {}".format(car_type, stdev*1.96))


    # Построение модели
    model = LinearRegression().fit(X_train, y_train)

    # Оценка R2 модели
    R2_train = model.score(X_train, y_train)
    print("Train R2 for model {}: {}".format(car_type, R2_train))

    R2_test = model.score(X_test, y_test)
    print("Test R2 for model {}: {}".format(car_type, R2_test))

    # Оценка MAE модели
    predictions_train = model.predict(X_train)
    MAE_train = metrics.mean_absolute_error(y_train, predictions_train)
    print("Train MAE for model {}: {}".format(car_type, MAE_train))

    predictions_test = model.predict(X_test)
    MAE_test = metrics.mean_absolute_error(y_test, predictions_test)
    print("Test MAE for model {}: {}".format(car_type, MAE_test))

    coefficients = pd.concat([pd.DataFrame(X_train.columns), pd.DataFrame(np.transpose(model.coef_))], axis=1)
    print(coefficients.head(10))
    errors = y_train - predictions_train

    plt.figure()
    plt.hist(errors, bins=30, density=True)
    plt.xlabel('Ошибки')
    plt.title(car_type)
    plt.show()

    # Расчет доверительного интервала прогноза
    stdev = np.sqrt(sum((predictions_train - y_train) ** 2) / (len(y_train) - 2))
    stats = pd.DataFrame([[car_type, stdev * 1.96, R2_train, MAE_train]],
                         columns=['Model', "CI (95%)", 'R2', 'MAE'])
    stat_df = stat_df.append(stats)
    with open(model_dir + "%s_model.pkl" % car_type, "wb") as file:
        pickle.dump(model, file)

stat_df.to_csv("stats.csv")
