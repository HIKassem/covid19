"""
Data source:
https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide

Author: Hassan Kassem
"""

import os
import pandas as pd
import urllib.request as urllib
import matplotlib.pyplot as plt
import numpy as np
import datetime


class DataSource():
    def __init__(self, date):
        self._url = \
        f"https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-{date.strftime('%Y-%m-%d')}.xlsx"
        self._file_name = self._url.split("/")[-1]
        self._req_date = date

    def data(self):
        data = pd.read_excel(self._file_name, parse_dates=True, index_col=0)
        return data

def getData(date):
    """ returns data of requested date or one day before if not available """
    
    try:
        data_source = DataSource(date)
        _ = urllib.urlretrieve(data_source._url, data_source._file_name)
        sel_date = date
    except:
        day_before = date - datetime.timedelta(days=1)
        data_source = DataSource(day_before)
        _ = urllib.urlretrieve(data_source._url, data_source._file_name)
        sel_date = day_before

    return sel_date, data_source.data()

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

def main():
    
    # country code, geoID
    ccodes = ["DE", "IT", "KR", "UK", "ES", "EG", "US"]
    # start from min_count of cases
    min_count = 100
    # number of days for moving average
    nd = 5
    # growth rate of expononetion function line
    gr  = 0.25
    # figure dpi
    in_dpi = 100


    # get today data or day before if not available
    today = datetime.datetime.today()
    date, data = getData(today)
    print(f"Latest data as reported on {date.strftime('%d-%m-%Y')}")
    print(data.head())
    figs, axs = plt.subplots(1, 2, figsize=(1536/in_dpi, 759/in_dpi), dpi=in_dpi)

    for co in ccodes:
        # dataFrame of each geoID
        df = data[data.geoId == co]
        # death rate
        rate = df.deaths.sum()/df.cases.sum()
        print(f"{co} death rate: {np.round(rate*100, 3)}%")
        # find nearest index if min_count
        st = df.iloc[(df.cases[::-1].cumsum()[::-1]-min_count).abs().argsort()[:1]]
        # cumulative cases ordered
        cases = df.cases[::-1].cumsum()[::-1]
        # cases = cases['2020-03-20':st]

        # left plot, cumsum vs days from min_count
        axs[0].semilogy(
            np.flip(cases.loc[:st.index[0]].values),
            label=f"{co}, (death rate: {np.round(rate*100, 1)}%), {df.cases.sum()} cases")
        # right plot, ma of new cases vs ma cumsum cases
        axs[1].loglog(
            moving_average(np.flip(cases.loc[:st.index[0]].values), nd),
            moving_average(np.flip(df.cases.loc[:st.index[0]].values), nd)
        )
    # exponential function
    d = np.linspace(0,30,50)
    axs[0].plot(d, 100*np.exp(gr*d), '--k', label=f"{gr*100}% exponential growth")
    axs[0].legend()

    axs[0].set_title(date.strftime('%d-%m-%Y'))
    axs[1].set_title(f"Moving average window {nd} days")

    now = datetime.datetime.now().isoformat(timespec='minutes')
    figs.suptitle(
        f"source: www.ecdc.europa.eu, accessed {now}. By: Hassan Kassem", fontsize=8)
    
    axs[0].set_ylabel("Cumulative cases")
    axs[0].set_xlabel(f"Days from {min_count}th case")

    axs[1].set_xlabel("Cumulative cases")
    axs[1].set_ylabel("New cases")


    # axs[0].grid()
    _ = [ax.grid() for ax in axs]

    axs[0].set_xlim(0)
    axs[0].set_ylim(min_count)

    # save figure
    plt.savefig(f"{date.strftime('%Y%m%d')}_plot.png",
        bbox_inches='tight', dpi=in_dpi)

    # show plot
    plt.show()

if __name__ == "__main__":
    main()

