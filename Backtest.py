import pybithumb
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt

def make_xlsx_ror(k, ticker, target_vol, start_date, end_date):

    print(ticker)
    print(pybithumb.get_tickers())

    df = pybithumb.get_ohlcv(ticker)
    df = df.loc[start_date:end_date]

    # 연도 적용
    # df = df['2021']

    # 변동성 계산
    df['stb'] = ((df['high'] - df['low']) / df['open']) * 100
    df['stb5'] = df['stb'].rolling(window=5).mean().shift(1)



    # 전략적용 - 상승장
    df['ma5'] = df['close'].rolling(window=5).mean().shift(1)
    df['bull'] = df['open'] > df['ma5']


   # 전략 적용 - 변동성 돌파
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)


    # 수익률 계산
    fee = 0.0032

    df['ror'] = np.where((df['high'] > df['target']) & df['bull'],
                         df['close']/df['target'] - fee, 1)



    df['vol'] = target_vol / df['stb5']
    df.loc[(df.vol > 1), 'vol'] = 1
    df['invest'] = df['vol'] * df['ror'] + (1- df['vol'])
    df['hpr'] = df['ror'].cumprod()
    df['hpr_invest'] = df['invest'].cumprod()

    ''' # MDD 계산
    df['hpr'] = df['ror'].cumprod()
    df['dd'] = (df['hpr'].cummax() - df['hpr']/ df['hpr'].cummax() * 100)
    MDD = df['dd'].max()'''


    '''    # 승률 계산
    df['win'] = np.where(df['ror'] < 1, False, True)
    a = df['win'].value_counts()
    print(a)
    '''
    return df



'''
def get_today_top5(index):
    book = []
    tickers = pybithumb.get_tickers()
    for ticker in tickers:
          df = pybithumb.get_ohlcv(ticker)
          df = df.iloc[index-6:]
          last_ma5 = df['close'].mean()
          score = (df['open'] - last_ma5) / last_ma5
          book.append((ticker, score))

    book_sorted = sorted(book, key=lambda x:x[1], reverse=True)
    return book_sorted[:5]

'''



if __name__ == '__main__':

    # 변수 모음 =====================
    start_date = '2013-12-27'
    end_date = '2021-10-12'
    ticker_list = ['BTC', 'ETH', 'XRP', 'BTG']
    target_vol = 2
    k = 0.5
    # ===============================


    # 파일 만들기
    writer = pd.ExcelWriter('./coin.xlsx')

    # 파일 추가
    for ticker in ticker_list:

        df = make_xlsx_ror(k, ticker, target_vol,start_date, end_date)
        df.to_excel(writer, sheet_name=ticker)
        writer.save()

    # 자산 돌리기

    main_df = pd.DataFrame(columns=['time'])
    for ticker in ticker_list:
        df = pd.read_excel('./coin.xlsx', sheet_name=ticker, engine='openpyxl')
        df_new = df.loc[:, ['time', 'invest']]

        df_new = df_new.rename(columns ={'invest':str(ticker)})

        main_df = pd.merge(main_df, df_new, how='outer', on='time')

    main_df.to_excel('test.xlsx')

    main_df= main_df.fillna(1)

    x = 0
    for ticker in ticker_list:
        if x == 0:
            main_df['sum'] = main_df[ticker]
            x = x+1
        else :
            main_df['sum'] = main_df['sum'] + main_df[ticker]
    main_df['sum'] = main_df['sum'] / len(ticker_list)


    main_df['hpr'] = main_df['sum'].cumprod()
    main_df['dd'] = ((main_df['hpr'].cummax() - main_df['hpr']) / main_df['hpr'].cummax()) * 100
    MDD = main_df['dd'].max()
    diff = main_df['time'].iloc[-1] - main_df['time'].iloc[0]
    diff = diff.days / 365
    hpr = main_df['hpr'].iloc[-1]
    cagr = ((hpr**(1/diff)) -1) * 100

    # 승률 계산
    main_df['win'] = np.where(main_df['sum'] < 1, False, True)
    a = main_df['win'].value_counts()

    # 매매횟수
    main_df['buy'] = np.where(main_df['sum'] ==1, False, True)
    b = main_df['buy'].value_counts()

    main_df.to_excel('result.xlsx')
    print('MDD의 값은 : ' )
    print(MDD)
    print('기간수익률:' + str(hpr))
    print('CAGR: ')
    print(cagr)
    print('이긴횟수: ')
    print(a)
    print('매매횟수: ')
    print(b)
    plt.plot(main_df['time'], main_df['hpr'])
    plt.show()












