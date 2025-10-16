# coding: utf-8

# ## Active Shirleyの出力ファイルからAIC, BICを計算

import numpy as np
from scipy import signal
from matplotlib import pyplot as plt
import pandas as pd
import math
import subprocess

# fitting_result_file = './result_peak_search_mSG5.csv'
# #fitting_result_file = './result_peak_search_mSG5_old.csv'
# fitting_parameter_file = './parameters_peak_search_mSG5.csv'
#
# fitting_result_file = './result_peak_search_mSG27.csv'
# fitting_parameter_file = './parameters_peak_search_mSG27.csv'

def calc_AIC_BIC(fitting_result_file, fitting_parameter_file, idHigherS=-1, idLowerS=-1):
    #高BEと低BEのインデックスを読み込む
#     f = "./20181108g_work_changewindow_500times/COMPRO__Zxxx__Al2p__Aluminium_Oxide__AlX__00002258/result_peak_search_mSG001.csv"
#     df = pd.read_table(fitting_result_file, delimiter="=", header=None, skiprows=lambda x: x not in [0, 1])
#     df = pd.read_table(fitting_result_file, delimiter="=", header=None, nrows=2)
    df = pd.read_csv(fitting_result_file, delimiter="=", header=None, nrows=2)
    idHigherOrg = df[1][0]
    idLowerOrg = df[1][1]

    #入力スペクトルおよびフィッティングスペクトル読み込み
    df = pd.read_csv(fitting_result_file, comment='#')
    # print(df.dtypes)

    # 解析範囲以外を削除
    if(idHigherS>=0 and idLowerS>= 0):
        # df1 = df[idHigherS:(idLowerS+1)]
        # numData = idLowerS - idHigherS + 1
        idHigher = idHigherS
        idLower = idLowerS
    else:
        # df1 = df[np.isnan(df.background) == False]
        df1 = df[pd.isnull(df.background) == False]

        df2 = df1
        if type(df1.background[0]) == object:
            df2 = df1[df1.background != "-nan(ind)"]
            # df2 = df1[df1.iloc[:,3] != '-nan(ind)']
        else:
            df2 = df1

        # print(df2.background)
        numData = len(df2.index)
        # print("numData=", numData)
        if(numData == 0):
            print("Error. All background data is NaN.")
            return

        # idHigher, idLower を読み込み、データ数を取得
        mycmd = 'grep "# idHigher" %s | cut -d" " -f4' % (fitting_result_file)
        idHigher = subprocess.call(mycmd, shell=True)
        mycmd = 'grep "# idLower" %s | cut -d" " -f4' % (fitting_result_file)
        idLower = subprocess.call(mycmd, shell=True)
        # idLower = commands.getoutput(mycmd)

    numData = idLower - idHigher + 1
    # print("idHigher=", idHigher)
    # print("idLower=", idLower)
    # print("numData=", numData)
    # print("file,idHigher,idLower,numData = %s, %d, %d, %d" % (fitting_result_file, idHigher, idLower, numData) )
    
    # 始点と終点のエネルギー
    energyHigher = df["Binding_Energy(eV)"][idHigher]
    energyLower = df["Binding_Energy(eV)"][idLower]
    
    energyHigherOrg = df["Binding_Energy(eV)"][idHigherOrg]
    energyLowerOrg = df["Binding_Energy(eV)"][idLowerOrg]

    df1 = df.iloc[idHigher:(idLower+1),:]
    
    # バックグラウンドに負の値があれば評価から外す
    if np.any(df1.background < 0):
        print("Error. Background has negative value.")
        return

    # フィッティングパラメータ読み込み（ピーク本数を取得）
    dfp = pd.read_csv(fitting_parameter_file)

    # ピーク本数およびパラメータ数
    numPeak = len(dfp.index)
    numParam = 4 * numPeak + 2
    # print("numPeak=", numPeak)
    # print("numParam=", numParam)

    # 最小半値半幅
    min_HWHM = dfp.width[dfp.width.idxmin()]
    # print("min_HWHM=", min_HWHM)

    # 一様なガウスノイズを仮定して、ノイズの分散および逸脱度を計算
    variance_gauss = ((df1.spectrum - df1.fitting)**2).mean()
    deviance_gauss = numData * (1.0 + np.log(2.0 * np.pi * variance_gauss))
    # print("variance_gauss=", variance_gauss)
    # print("deviance_gauss=", deviance_gauss)

    # そのときのAIC, BIC
    aic_gauss = deviance_gauss + 2.0 * numParam
    bic_gauss = deviance_gauss + np.log(numData) * numParam
    # print("aic_gauss=", aic_gauss)
    # print("bic_gauss=", bic_gauss)

    # 強度に依存したガウスノイズを仮定して，分散の最尤推定。
    # スケーリング因子を計算。逸脱度を計算
    param_b = ((df1.spectrum - df1.fitting)**2 / df1.fitting).mean()
    scaling_pgauss = 1.0 / param_b
#    deviance_pgauss = (np.log(df1.fitting)).sum() + numData * (1.0 + np.log(2.0 * np.pi * scaling_pgauss))
    # そのときのAIC, BIC
#    aic_pgauss = deviance_pgauss + 2.0 * numParam
#    bic_pgauss = deviance_pgauss + np.log(numData) * numParam

    # 強度に依存したガウスノイズを仮定して，分散の最尤推定。
    # スケーリングを行うとデータそのものが変わってしまうため，AIC, BIC計算には不適切
    # スケーリングは行わずに逸脱度を計算
    deviance_pgauss = (np.log(df1.fitting)).sum() + numData * (1.0 + np.log(2.0 * np.pi * param_b))
    # そのときのAIC, BIC
    aic_pgauss = deviance_pgauss + 2.0 * numParam
    bic_pgauss = deviance_pgauss + np.log(numData) * numParam
    

    # ポアソンノイズを仮定して、逸脱度を計算
    # 縦軸の単位がカウント数の場合にのみ意味がある
    # 対数ガンマ関数は配列計算できないので tmp 使用
    #df1.spectrum - df1.fitting * np.log(df1.spectrum) + math.lgamma(df1.fitting + 1.0)

    # tmp = []
    # for y in df1.fitting:
    #     tmp.append(math.lgamma(y + 1.0))
    #tmp = [ math.lgamma(y + 1.0) for y in df1.fitting ]
    #deviance_poisson = 2.0 * sum(df1.spectrum - df1.fitting * np.log(df1.spectrum) + tmp)
    # print("deviance_poisson=", deviance_poisson)
    
    tmp = [ math.lgamma(y + 1.0) for y in df1.spectrum ]
    deviance_poisson = 2.0 * sum(df1.fitting - df1.spectrum * np.log(df1.fitting) + tmp)

    # そのときのAIC, BIC
    aic_poisson = deviance_poisson + 2.0 * numParam
    bic_poisson = deviance_poisson + np.log(numData) * numParam
    # print("aic_poisson=", aic_poisson)
    # print("bic_poisson=", bic_poisson)



    # カイ二乗
    chi2 = sum((df1.spectrum - df1.fitting)**2 / df1.fitting)

    # Reduced カイ二乗
    reduced_chi2 = chi2 / (numData - numParam)

    # print(numData, numPeak, numParam, variance_gauss, deviance_gauss, aic_gauss, bic_gauss, deviance_poisson, aic_poisson, bic_poisson)
    # return [numData, numPeak, numParam, variance_gauss, deviance_gauss, aic_gauss, bic_gauss, deviance_poisson, aic_poisson, bic_poisson, chi2, reduced_chi2, min_HWHM, idHigher, idLower]
    # return [numData, numPeak, numParam, variance_gauss, deviance_gauss, aic_gauss, bic_gauss, deviance_poisson, aic_poisson, bic_poisson, chi2, reduced_chi2, min_HWHM, idHigher, idLower, energyHigher, energyLower, idHigherOrg, idLowerOrg, energyHigherOrg, energyLowerOrg]
    return [numData, numPeak, numParam, variance_gauss, deviance_gauss, aic_gauss, bic_gauss, deviance_poisson, aic_poisson, bic_poisson, scaling_pgauss, deviance_pgauss, aic_pgauss, bic_pgauss, chi2, reduced_chi2, min_HWHM, idHigher, idLower, energyHigher, energyLower, idHigherOrg, idLowerOrg, energyHigherOrg, energyLowerOrg]
