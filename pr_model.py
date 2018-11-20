# Wrapper around data model
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn import linear_model

import scipy.stats

import glob, os, math
from functools import reduce

plt.style.use('bmh')

def read_symbol_history(sym):
    df = pd.read_csv('daily/table_' + sym.lower() + '.csv', 
        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'])
    df.set_index('date')
    df.date = pd.to_datetime(df['date'], format='%Y%m%d')
    return df    

def read_entire_market():
    all_files = glob.glob(os.path.join('daily', '*.csv'))
    dfs = [pd.read_csv(f, 
        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume']) for f in all_files]
    df = reduce (lambda x, y: x.add(y, fill_value = 0), dfs) # BUG: This will add dates
    return df

def plot_symbol_history(sym):
    df = read_symbol_history(sym)
    plt.plot(df.date, df.close, linewidth=1)
    plt.title(sym + ' Price History')
    plt.xlabel('Date')
    plt.ylabel('Price ($)')
    plt.show()

def plot_two_symbol_histories(sym1, sym2):
    df1 = read_symbol_history(sym1)
    df2 = read_symbol_history(sym2)
    
    plt.plot(df1.date, df1.close, linewidth=1)
    plt.plot(df2.date, df2.close, linewidth=1)
    plt.title(sym1 + ' vs. ' + sym2)
    plt.xlabel('Date')
    plt.ylabel('Price ($)')
    plt.show()

def plot_entire_market():
    df = read_entire_market()

    plt.plot(df.close, linewidth=1)
    plt.title('Entire Market Price History')
    plt.xlabel('Date')
    plt.ylabel('Price ($)')
    plt.show()


def add_daily_returns(df):
    df['daily_return'] = ((df.close - df.open) / df.open) * 100

def plot_return_distribution(sym, print_table=False):
    if (sym == 'MARKET'):
        df = read_entire_market()
    else:
        df = read_symbol_history(sym)
    add_daily_returns(df)

    _, ax1 = plt.subplots()
    df.daily_return.plot.hist(bins=75, ax = ax1)

    # fit to a normal distribution and plot that as well alongside the
    # histogram; with a second set of axes so scale isn't an issue
    ax2 = ax1.twinx()
    mu, std = scipy.stats.norm.fit(df.daily_return.values)
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = scipy.stats.norm.pdf(x, mu, std)
    ax2.plot(x, p, 'k', linewidth=1)
    title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
    plt.title(title)

    if print_table:
        print (sym)
        print ('Mean: %.2f' % mu)
        print ('Std: %.2f' % std )

    plt.show()

def plot_return_timeline(sym):
    if (sym == 'MARKET'):
        df = read_entire_market()
    else:
        df = read_symbol_history(sym)

    add_daily_returns(df)
    df.daily_return.plot()
    plt.show()

def plot_comparison(sym_1, sym_2='MARKET'):

    # switch around the indices here, purpose of this is to show how
    # sym_2 can predict sym_1, not the other way around (as sym_2 defaults
    # to 'MARKET')
    df_2 = read_symbol_history(sym_1)

    if (sym_2 == 'MARKET'):
        df_1 = read_entire_market()
    else:
        df_1 = read_symbol_history(sym_2)

    add_daily_returns(df_1)
    add_daily_returns(df_2)

    x = df_1.daily_return.values.reshape(-1, 1)
    y = df_2.daily_return.values.reshape(-1, 1)
    
    regr = linear_model.LinearRegression()
    regr.fit(x, y)
    print ("Coefficients: ", regr.coef_)
    print ("Intercept: ", regr.intercept_)

    plt.plot(df_1.daily_return, df_2.daily_return, '.', markersize=2)
    plt.plot(x, regr.predict(x), linewidth=1)

    plt.title('Correlation of ' + sym_1 + ' vs. ' + sym_2)
    plt.xlabel(sym_2 + ' Daily Return')
    plt.ylabel(sym_1 + ' Daily Return')
    plt.show()

def plot_risk_return_comparison_whole_market():
    all_files = glob.glob(os.path.join('daily', '*.csv'))
    dfs = [pd.read_csv(f, 
        names=['date', 'time', 'open', 'high', 'low', 'close', 'volume']) for f in all_files]


    means = []
    stds = []
    for df in dfs:
        add_daily_returns(df)
        desc = scipy.stats.describe(df.daily_return.values)
        means.append(desc.mean)
        stds.append(math.sqrt(desc.variance))
    
    plt.plot(stds, means, 'o')
    plt.xlabel("Standard Deviation of Daily Returns")
    plt.ylabel("Daily Return")
    plt.show()

def construct_two_stock_portfolio(sym_1, sym_2, show_frontier=False):
    df_1 = read_symbol_history(sym_1)
    df_2 = read_symbol_history(sym_2)
    
    add_daily_returns(df_1)
    add_daily_returns(df_2)

    desc = scipy.stats.describe(df_1.daily_return.values)
    mean_1 = desc.mean
    std_1 = math.sqrt(desc.variance)

    desc = scipy.stats.describe(df_2.daily_return.values)
    mean_2 = desc.mean
    std_2 = math.sqrt(desc.variance)

    print ('%s: Mean (%.2f); Std (%.2f)' % (sym_1, mean_1, std_1))
    print ('%s: Mean (%.2f); Std (%.2f)' % (sym_2, mean_2, std_2))

    # The two outcomes where it's 100% invested into a single stock
    plt.plot(std_1, mean_1, 'o')
    plt.plot(std_2, mean_2, 'o')

    if show_frontier:
        # The efficient frontier
        weights_1 = np.linspace(-1, 2, 100)
        weights_2 = 1 - weights_1
        
        # E(x) is weighted average
        all_returns = weights_1 * mean_1 + weights_2 * mean_2

        # Variance of sum of 2 variables: a^2 Var(x) + b^2 Var (y) + 2ab Cov(X, Y)
        var_1 = std_1 * std_1
        var_2 = std_2 * std_2
        cov_1_2 = np.cov(np.array([df_1.daily_return.values, df_1.daily_return.values]), bias=True, rowvar=False)[0, 1]

        all_variances = weights_1**2 * var_1 + weights_2**2 * var_2 + 2 * weights_1 * weights_2 * cov_1_2
        all_stds = np.sqrt(all_variances)

        plt.plot(all_stds, all_returns, 'k', linewidth=1)
        
    plt.xlim(xmin=0)
    plt.ylim(ymin=0)
    plt.show()

construct_two_stock_portfolio('AAPL', 'MSFT', show_frontier=True)