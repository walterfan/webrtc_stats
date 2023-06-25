import matplotlib
matplotlib.use('Agg')
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from pytz import timezone
from datetime import datetime

class Plotter:
    def __init__(self, chart_file, width=24, height=20) -> None:
        self._chart_file = chart_file
        self._width = width
        self._height = height
        self._csv_file = self.chart_file[:-4] + '.csv'

    def draw_charts(self, df, chart_fields, abscissa="timestamp", chart_type="line"):
        plt.style.use('seaborn-v0_8-whitegrid')
        chart_count = len(chart_fields)

        fig = plt.figure(figsize=(self._width, self._height * chart_count))
        font = {'weight' : 'bold', 'size'   : 18}
        plt.rc('font', **font)

        i = 0

        for chart_field in chart_fields:
            if chart_field not in df:
                print(f'{chart_field} not in this catagory, skip...')
                continue

            i = i + 1
            ax = fig.add_subplot(chart_count, 1, i)
            self.draw_chart(ax, df, chart_field, abscissa, chart_type)

        fig.savefig(self._chart_file)
        plt.close()

    def draw_chart(self, ax,  df, chart_field, abscissa="timestamp", chart_type="line"):
        print("draw chart for {}, {}".format(abscissa, chart_field))
        plt.title(chart_field)
        plt.xlabel(abscissa)
        plt.ylabel(chart_field)
        plt.grid(True)
        plt.xticks(rotation=30)

        date_form = DateFormatter("%H:%M:%S")
        ax.xaxis.set_major_formatter(date_form)

        if chart_type == "scatter":
            ax.scatter(df[abscissa], df[chart_field], marker='o', label=chart_field)
        elif chart_type == "bar":
            ax.bar(df[abscissa], df[chart_field], label=chart_field)
        else:
            ax.plot(df[abscissa], df[chart_field], marker='.', label=chart_field)

        begin_time = df[abscissa][0]
        for a, b in zip(df[abscissa], df[chart_field]):
            if (a - begin_time).seconds >= 5 or a == begin_time:
                begin_time = a
                ax.text(a, b, b, ha='center', va='bottom', fontsize=8, rotation=45)

        label_format = '{:,.0f}'
        ticks_loc = ax.get_yticks().tolist()
        ax.yaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
        ax.set_yticklabels([label_format.format(x) for x in ticks_loc])
