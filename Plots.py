import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import statsmodels.formula.api as smf

plt.style.use('ggplot')

types = ['econ', 'econ_plus', 'business', 'bistro', 'first_class']
types_names = {
    'econ': "Эконом",
    'econ_plus': "Эконом Плюс",
    'business': "Бизнес",
    'bistro': "Бистро",
    'first_class': "Первый класс"
}
dataDir = "../Data"
df = pd.read_csv(dataDir + "/dataset.csv")


# Фукнция для построения средних цен с параболой
def plot_prices():
    for _i, car_type in enumerate(types):
        type_df = df[df[car_type] == 1].copy()
        Q1 = type_df['ceni'].quantile(0.25)
        Q3 = type_df['ceni'].quantile(0.75)
        IQR = Q3 - Q1
        lower_range = Q1 - (1.5 * IQR)
        upper_range = Q3 + (1.5 * IQR)
        type_df = type_df[type_df['ceni'] > lower_range]
        type_df = type_df[type_df['ceni'] < upper_range]
        type_df['t3'] = type_df['t'] ** 3

        mean_ceni = type_df[['t', 'ceni']].groupby('t').agg('mean')
        mean_ceni['tsquare'] = mean_ceni.index ** 2
        mean_ceni['t'] = mean_ceni.index

        plt.figure()
        model_agg = smf.ols('ceni ~ t + tsquare', data=mean_ceni).fit()
        plt.scatter(mean_ceni.index, mean_ceni['ceni'])
        plt.xlabel('Дней до отправления')
        plt.ylabel('Средняя цена')
        parable = mean_ceni['t'] * model_agg.params['t'] + mean_ceni['tsquare'] * model_agg.params['tsquare'] + \
                  model_agg.params['Intercept']
        plt.plot(mean_ceni['t'], parable, color='blue')
        plt.title(types_names[car_type])
        plt.show()


# Функция для построения ящиков в усами
def plot_boxplots():
    plt.figure()
    data_to_plot = []
    for _i, car_type in enumerate(types):
        type_df = df[df[car_type] == 1].copy()
        data_to_plot.append(type_df['ceni'])

    plt.boxplot(data_to_plot, labels=types)
    plt.show()
    plt.figure()
    plt.boxplot(data_to_plot, labels=types, autorange=True)
    plt.show()


# Функция для построения гистограмм цен после исключения выбросов
def plot_hist_outliers():
    plt.figure()
    for _i, car_type in enumerate(types):
        type_df = df[df[car_type] == 1].copy()

        # Гистограмы до фильтрации
        plt.figure()
        plt.hist(type_df['ceni'], bins=15, density=True)
        plt.xlabel('Цены')
        plt.title(types_names[car_type])
        plt.show()

        #Фильтрация выбросов
        Q1 = type_df['ceni'].quantile(0.25)
        Q3 = type_df['ceni'].quantile(0.75)
        IQR = Q3 - Q1
        lower_range = Q1 - (1.5 * IQR)
        upper_range = Q3 + (1.5 * IQR)
        type_df = type_df[type_df['ceni'] > lower_range]
        type_df = type_df[type_df['ceni'] < upper_range]

        # Гистограммы после фильтрации
        plt.figure()
        plt.hist(type_df['ceni'], bins=15, density=True)
        plt.xlabel('Цены')
        plt.title(types_names[car_type])
        plt.show()


if __name__ == "__main__":
    plot_prices()
    plot_boxplots()
    plot_hist_outliers()
