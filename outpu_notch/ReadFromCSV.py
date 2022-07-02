
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import statsmodels.api as sm
import pyecharts.options as opts
from pyecharts.charts import Line

class ReadFromCSV:

    def read(self, pathname, rowindex, todelete, todeleteRow, reverse):
        data = pd.read_csv(pathname, encoding="gbk")
        data = data.drop(data.filter(regex=todelete).columns, axis=1)
        if reverse == 1:
            data = data[~data['时间'].str.contains(todeleteRow, regex=True)].iloc[::-1]
        else:
            data = data[~data['时间'].str.contains(todeleteRow, regex=True)]
        data = data.rename(columns={'电力、热力生产和供应业增加值同比增长(%)': '电力、热力的生产和供应业增加值同比增长(%)'})
        #print(data.columns)
        # data = np.delete(data, data[data['时间'].str.contains(todeleteRow, regex=True)].index, axis=0)
        # data = np.delete(data, axis=0)
        # print(data.index)
        # print(data.columns)
        # print(data)
        return data

    def combine(self, *data):
        data_concat = pd.concat(data, axis=0)
        # pd.set_option("display.max_columns", None)
        # pd.set_option("display.max_rows", None)
        # print(data_concat)
        return data_concat

    def drawTend(self, data, timeCoulum, *columns):
        for column in columns:
            column = column.replace("(", "\\(")
            column = column.replace(")", "\\)")
            lsData = data.loc[:, data.columns.str.contains(timeCoulum + "|" + column, regex=True)]
            timeCoulums = lsData[timeCoulum];

            #print(lsData)
            #ha滤波
            columnAlia = column.replace("\\", "")
            originData = np.array(lsData[columnAlia])
            #年度100，季度1600，月度14400
            #targetData = self.hp(originData, 100)
            cycle, trend = sm.tsa.filters.hpfilter(originData, 14400)
            print(cycle)
            columnsLs = []
            columnsLs.append(columnAlia)
            ansData = pd.DataFrame(cycle, index=timeCoulums, columns=columnsLs)
            #画图
            #plt.rcParams['font.sans-serif'] = ['SimHei']

            # fig,ax1 = plt.subplots()
            # ax2 = ax1.twinx()
            # ax1.plot(timeCoulums, originData, 'g--')
            # ax2.plot(timeCoulums, targetData, 'b--')

           # plt.plot(originData, label="origin")
            #plt.plot(ansData, label="filter")
           # oy.set_ylim(0, 50)
            #fy.set_ylim(-1,1)

            # ansData.plot()
            # lsData.set_index([timeCoulum], inplace=True)
            # lsData.plot()
            # plt.show()

            c = (
                Line(init_opts=opts.InitOpts(width="2000px", height="750px"))
                .add_xaxis(list(timeCoulums))
                .add_yaxis("short_cycle", list(cycle))
                .add_yaxis("short_trend", list(trend))
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=columnAlia),
                    tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")
                    )
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                .render(columnAlia + "趋势.html")
        )

    def drawLine(self, data, timeCoulum, *columns):
        for column in columns:
            column = column.replace("(", "\\(")
            column = column.replace(")", "\\)")
            lsData = data.loc[:, data.columns.str.contains(timeCoulum + "|" + column, regex=True)]
            timeCoulums = lsData[timeCoulum];

            #print(lsData)
            #ha滤波
            columnAlia = column.replace("\\", "")
            originData = np.array(lsData[columnAlia])
            #年度100，季度1600，月度14400
            #targetData = self.hp(originData, 100)

            c = (
                Line(init_opts=opts.InitOpts(width="2000px", height="750px"))
                .add_xaxis(list(timeCoulums))
                .add_yaxis("short_cycle", list(originData))
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=columnAlia),
                    tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")
                    )
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                .render(columnAlia + "趋势.html")
        )

    def hp(self, ts, lamd=10):
        def D_matrix(N):
            D = np.zeros((N-1, N))
            D[:, 1:] = np.eye(N-1)
            D[:, :-1] = np.eye(N-1)
            return D
        N = len(ts)
        D1 = D_matrix(N)
        D2 = D_matrix(N - 1)
        D = D2 @ D1
        g = np.linalg.inv((np.eye(N) + lamd * D.T@D)) @ ts
        return g

#工业产值缺口
def industry_leak():
    readUtil = ReadFromCSV()
    data2006 = readUtil.read("E:\economic_data\macroeconomic\China\output_notch2006-2011.csv", "时间", "累计", r"年(1|2)月", 1)
    data2012 = readUtil.read("E:\economic_data\macroeconomic\China\output_notch2012-2017.csv", "时间", "累计", r"年(1|2)月", 1)
    data2018 = readUtil.read("E:\economic_data\macroeconomic\China\output_notch2018-2022.csv", "时间", "累计", r"年(1|2)月", 1)

    dataAll = readUtil.combine(data2006, data2012, data2018)
    #dataAll.to_csv("E:\economic_data\macroeconomic\China\output_notchAll.csv")
    readUtil.drawTend(dataAll, "时间",
                      '煤炭开采和洗选业增加值同比增长(%)',
                      '石油和天然气开采业增加值同比增长(%)',
                      '黑色金属矿采选业增加值同比增长(%)',
                      '有色金属矿采选业增加值同比增长(%)',
                      '非金属矿采选业增加值同比增长(%)',
                      '其他采矿业增加值同比增长(%)')

#固定资产投资
def fiex_investment():
    readUtil = ReadFromCSV()
    data = readUtil.read("E:\economic_data\macroeconomic\China\\fix_investment.csv", "时间", "x", r"x", 1)
   # print(data)
    readUtil.drawTend(data, "时间", '固定资产累计同比增长(%)')

#房地产投资
def house_investment():
    readUtil = ReadFromCSV()
    data = readUtil.read("E:\economic_data\macroeconomic\China\house_investment.csv", "时间", "x", r"x", 1)
    # print(data)
    readUtil.drawTend(data, "时间", '房地产投资累计增长(%)')

def loan():
    readUtil = ReadFromCSV()
    data1 = readUtil.read("E:\economic_data\macroeconomic\China\loan_nonfinance_short.csv", "时间", "x", r"x", 0)
    readUtil.drawLine(data1, "时间", '非金融短线贷款')
    data2 = readUtil.read("E:\economic_data\macroeconomic\China\loan_nonfinance_long.csv", "时间", "x", r"x", 0)
    readUtil.drawLine(data2, "时间", '非金融中长期贷款')



if __name__ == '__main__':
    loan()

