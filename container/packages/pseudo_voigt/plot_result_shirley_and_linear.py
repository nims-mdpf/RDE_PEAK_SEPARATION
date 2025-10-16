#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import csv
# import json
# import collections as cl
import os, sys
from glob import glob
# from subprocess import check_call
# import subprocess
import shutil
import numpy as np
import pandas as pd
#import matplotlib.backends
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# fig = plt.figure()
import matplotlib.ticker as ticker
import matplotlib.cm as cm
from matplotlib.ticker import ScalarFormatter
from matplotlib.ticker import MaxNLocator
from time import sleep
import re

######## 並列計算用 #########
from multiprocessing import Pool
from multiprocessing import Process
######## 並列計算用 #########

from myfunc import calc_AIC_BIC

## ------------------------------------------------------------------
hasPIL = 1
if (hasPIL == 1):
    from PIL import Image, ImageDraw
    from io import BytesIO
    def savefig_by_PIL(fig, outpath, figdpi=1000):
        png1 = BytesIO()
        #fig.savefig(png1, format="png", bbox_inches='tight', dpi=figdpi)
        fig.savefig(png1, format="png", dpi=figdpi)
        png2 = Image.open(png1)
        print(f"Output to {outpath}")
        png2.save(outpath, compression="tiff_deflate")
        png1.close()
        png2.close()
        return
else:
    def savefig_by_PIL(fig, outpath, figdpi=1000):
        print("savefig_by_PIL() nothing to do")
        
## ------------------------------------------------------------------
def init_figure(nrow=1, ncol=1, figsize=(8, 6), sharey=False, tickstyle='sci'):
    plt.rcParams['font.size'] = 18
    plt.rcParams['font.family'] = 'Sans Serif'
#     plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['xtick.labelsize'] = plt.rcParams['font.size']
    plt.rcParams['ytick.labelsize'] = plt.rcParams['font.size']
    plt.rcParams['axes.labelsize']  = plt.rcParams['font.size']
    plt.rcParams['legend.fontsize'] = 14
    plt.rcParams['savefig.dpi'] = 200
    plt.rcParams['figure.dpi'] = 100
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    fig, axes = plt.subplots(nrow, ncol, figsize=figsize, sharey=sharey)
    if (nrow==1) & (ncol==1):
        axes = np.array([axes])

    for ax in axes:
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        if tickstyle == 'sci':
            ax.ticklabel_format(style="sci", axis="y", scilimits=(0,0))
        ax.minorticks_on()
        ax.tick_params(axis='both', which='both', top=True, right=True)
        ax.grid(ls=":")
    fig.tight_layout()
    
    if (nrow==1) & (ncol==1):
        return fig, axes[0]
    else:
        return fig, axes

## ------------------------------------------------------------------


def copy_and_rename(fname1, fname2):
    """
    Copy a file from fname1 to fname2 after checking the file exists or not
    """
    if os.path.exists(fname1):
        print("Copy from %s to %s" % (fname1, fname2))
        shutil.copy2(fname1, fname2)
    else:
        print("Not found %s" % fname1)

def plot_BIC_vs_numPeak(df3):
    fig, ax = init_figure(figsize=(8,6))
    ax.plot(df3['numPeak'], df3['bic_gauss'], 'o', mfc='None', label='BIC')
    ax.set_xlabel('Number of peaks')
    ax.set_ylabel('BIC')
    ax.grid(ls=":")
    # ax.legend(fontsize=14)
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.ticklabel_format(style="sci", axis="y", scilimits=(0,0))
    ax.minorticks_on()
    ax.tick_params(axis='both', which='both')
    ax.tick_params(axis='x', which='minor', bottom=False)
    fig.tight_layout()    
    pngfile = "BIC_vs_NumPeak.png"
    print("Output to ", pngfile)
    fig.savefig(pngfile)
    
## shinotsuka20190207
## 指定したディレクトリ dnm 以下にある "summary_evalFunc_vs_mSG.csv" を使い
## ピーク本数ごとにbic_gaussが最小となるモデルをピックアップする
## ピックアップするピーク本数は，少ない方から順にBIC最小のモデルのピーク本数まで．
## ただしそのときにピックアップするモデルが4以下であれば，5番目まで取り出すこと．
## ただしピーク本数でグループ化したときにピーク本数の種類が4以下であればその限りではない．
## それらの最適化モデルの図を名前を変えてコピーする
## 例： 
## BIC_rank{#1}_parameters_mSG{#2}_numPeak{#3}.csv
## BIC_rank{#1}_result_mSG{#2}_numPeak{#3}.csv
## BIC_rank{#1}_result_mSG{#2}_numPeak{#3}.png
def get_prefered_result_by_BIC_groupbypeaks(dnm, numPeakMax=None, figLevel=2):
    fnm = dnm + "summary_evalFunc_vs_mSG.csv"
    if not os.path.exists(fnm):
        print("Not found", fnm)
        return
        
    df3 = pd.read_csv(fnm, usecols=['numPeak', 'method', 'smoothing_point', 'bic_gauss'])
    
    csvfile = dnm + "summary_BIC.csv"
    print("Output to ", csvfile)
    df3.to_csv(csvfile, index=False)
    
    ## BIC vs. NumPeakをグラフ化
    if figLevel >= 1:
        # plot_BIC_vs_numPeak(df3)
        p = Process(target=plot_BIC_vs_numPeak, args=(df3,))
        p.start()
        p.join()

    ## --------------------------------------------------------------

    ## numPeakでくくり，それぞれbic_gaussが最小となる行だけをピックアップする
    df3p = df3.loc[df3.groupby('numPeak')['bic_gauss'].idxmin()]

    ## データをBIC順にソートし，上位5件までのうちの最大のピーク数をnumPeakPickupMaxとして取得する．
    numPeakPickupMax = df3p.sort_values('bic_gauss')[:5]['numPeak'].max()

    ## データをピーク本数順にソートする
    df3p.sort_values('numPeak', inplace=True)

    # ## numPeak <= numPeakMax の範囲に絞り込む
    # if numPeakMax is not None:
    #     df3p = df3p[df3p['numPeak'] <= numPeakMax]

    ## numPeak <= numPeakPickupMax の範囲に絞り込む
    df3p = df3p[df3p['numPeak'] <= numPeakPickupMax]

    ## インデックスを振り直す
    df3p.reset_index(drop=True, inplace=True)

    # ## BIC最小となるピーク本数のランク
    # rankAtMinBIC = df3p['bic_gauss'].idxmin() + 1
    # ## ランキング付けする最大順位
    # ## rankAtMinBICが5より大きい場合はそのピーク本数まで図を作成する
    # # rankMax = min(5, len(df3p))
    # rankMax = max(min(5, len(df3p)), rankAtMinBIC)

    # 全部取得する場合
    rankMax = len(df3p)

    ## rankMaxまでで切り取る
    df3p = df3p.iloc[:rankMax,:]

    ## bic_gaussの小さい順に並び替える。
    df3p = df3p.sort_values('bic_gauss', ascending=True)
    
    #print(df3p)
    #print("rankMax = ", rankMax)

    ## 第1位から第rankMax位までの図，パラメータファイル，スペクトルデータファイルを名前を変えてコピーする
    for i in np.arange(rankMax):
        smoothing_point = df3p[i:i+1]['smoothing_point'].values[0]
        numPeak = df3p[i:i+1]['numPeak'].values[0]
        method = df3p[i:i+1]['method'].values[0]
        rank = i + 1
        print(rank, smoothing_point, numPeak, method)

        
        rkWord = "rank%d" % rank
        smWord = "mSG%04d" % smoothing_point
        npWord = "numPeak%d" % numPeak
        
        fname1 = f"./{method}/parameters_peak_search_{smWord}.csv"
        fname2 = f"gbp_{rkWord}_{npWord}_{method}_{smWord}_parameters.csv"
        copy_and_rename(fname1, fname2)

        fname1 = f"./{method}/result_peak_search_{smWord}.png"
        fname2 = f"gbp_{rkWord}_{npWord}_{method}_{smWord}_result.png"
        copy_and_rename(fname1, fname2)

        fname1 = f"./{method}/result_peak_search_{smWord}.csv"
        fname2 = f"gbp_{rkWord}_{npWord}_{method}_{smWord}_result.csv"
        copy_and_rename(fname1, fname2)
        
        ## '#'で始まる行を削除する。Win/Linux共用とするためにシェルを使わない
        with open(fname2) as f:
            lines = [ l for l in f.readlines() if not l.startswith("#")]
        with open(fname2, 'wt') as f:
            f.write(''.join(lines))    

## shinotsuka20190207
## 指定したディレクトリ dnm 以下にある "summary_evalFunc_vs_mSG.csv" を使い
## BIC値が最も低いものから5番目までを選出する。
## それらの最適化モデルの図を名前を変えてコピーする
## 例： 
## BIC_rank{#1}_parameters_mSG{#2}_numPeak{#3}.csv
## BIC_rank{#1}_result_mSG{#2}_numPeak{#3}.csv
## BIC_rank{#1}_result_mSG{#2}_numPeak{#3}.png
def get_prefered_result_by_BIC(dnm, figLevel=2):
    """
    dnm: Directory name that ends with "/".
    Using "summary_evalFunc_vs_mSG.csv" under the directory,
    extract the first to fifth models from the lower BIC values.
    For each number of peaks, only a model with the lowest BIC is a candidate.
    The output files are 
        BIC_rank{#1}_parameters_mSG{#2}_numPeak{#3}.csv
        BIC_rank{#1}_result_mSG{#2}_numPeak{#3}.csv
        BIC_rank{#1}_result_mSG{#2}_numPeak{#3}.png
    where {#1} is a BIC ranking, {#2} is a number of smoothings, {#3} is a number of peaks 
    """
    fnm = dnm + "summary_evalFunc_vs_mSG.csv"
    if not os.path.exists(fnm):
        print("Not found", fnm)
        return
        
    df3 = pd.read_csv(fnm, usecols=['numPeak', 'method', 'smoothing_point', 'bic_gauss'])
    
    csvfile = dnm + "summary_BIC.csv"
    print("Output to ", csvfile)
    df3.to_csv(csvfile, index=False)
    
    ## BIC vs. NumPeakをグラフ化
    if figLevel >= 1:
        # plot_BIC_vs_numPeak(df3)
        p = Process(target=plot_BIC_vs_numPeak, args=(df3,))
        p.start()
        p.join()

#     ## 新しいデータフレームにする
#     df3p = df3
#     ## numPeakでくくり，それぞれbic_gaussが最小となる行だけをピックアップする
#     df3p = df3p.loc[df3p.groupby('numPeak')['bic_gauss'].idxmin()]
#     ## その結果をbic_gauss順にソートする
#     df3p.sort_values('bic_gauss', inplace=True)
    
    ## 単純にbic_gaussの小さい順に並び替える。
    df3p = df3.sort_values('bic_gauss', ascending=True)[0:5]    

#     csvfile = dnm + "summary_ranking_by_BIC.csv"
#     print("Output to ", csvfile)
#     df3p.to_csv(csvfile, index=False)
    
    ## ランキング付けする最大順位
    #rankMax = 5
    #rankMax = len(df3p)
    rankMax = min(5, len(df3p))
    #print("rankMax = ", rankMax)

    ## 第1位から第rankMax位までの図，パラメータファイル，スペクトルデータファイルを名前を変えてコピーする
    for i in np.arange(rankMax):
        smoothing_point = df3p[i:i+1]['smoothing_point'].values[0]
        numPeak = df3p[i:i+1]['numPeak'].values[0]
        method = df3p[i:i+1]['method'].values[0]
        rank = i + 1
        print(rank, smoothing_point, numPeak)
        
        rkWord = "rank%d" % rank
        smWord = "mSG%04d" % smoothing_point
        npWord = "numPeak%d" % numPeak
        
#         fname1 = dnm + "parameters_peak_search_%s.csv" % smWord
#         fname2 = dnm + "BIC_%s_%s_%s_%s_parameters.csv" % (rkWord, method, smWord, npWord)
        fname1 = f"./{method}/parameters_peak_search_{smWord}.csv"
        fname2 = f"BIC_{rkWord}_{method}_{smWord}_{npWord}_parameters.csv"
        copy_and_rename(fname1, fname2)
            
#         fname1 = dnm + "result_peak_search_%s.png" % smWord 
#         fname2 = dnm + "BIC_%s_%s_%s_%s_result.png" % (rkWord, method, smWord, npWord)
        fname1 = f"./{method}/result_peak_search_{smWord}.png"
        fname2 = f"BIC_{rkWord}_{method}_{smWord}_{npWord}_result.png"
        copy_and_rename(fname1, fname2)

#         fname1 = dnm + "result_peak_search_%s.csv" % smWord 
#         fname2 = dnm + "BIC_%s_%s_%s_%s_result.csv" % (rkWord, method, smWord, npWord)
        fname1 = f"./{method}/result_peak_search_{smWord}.csv"
        fname2 = f"BIC_{rkWord}_{method}_{smWord}_{npWord}_result.csv"
        copy_and_rename(fname1, fname2)

        ## '#'で始まる行を削除する。bashのsedコマンドを使う
        #shcommand = "bash -c '''sed -i '/^#/d' %s'''" % fname2
        #print(shcommand)
        #proc = subprocess.check_output(shcommand, shell=True)
        
        ## '#'で始まる行を削除する。Win/Linux共用とするためにシェルを使わない
        with open(fname2) as f:
            lines = [ l for l in f.readlines() if not l.startswith("#")]
        with open(fname2, 'wt') as f:
            f.write(''.join(lines))     
        


def plot_input_spectrum(path, ylim=None):
    #ファイル読み込み
    # path = './'+dir+'/'+dir+'.csv'
    # path = './'+dir+'.csv'
    if not os.path.exists(path):
        print('Warning:', path, 'is not exists')
        return

    print("Load from", path)

    df3 = pd.read_csv(path, header=None, comment='B')

    #PNGファイル出力
    # pngfile = './'+dir+'/input_spectrum2.png'
    pngfile = './input_spectrum2.png'
    print("Output to", pngfile)
    
    
#     plt.figure(figsize=(8,6))
#     plt.rcParams["font.size"] = 18
#     plt.plot(df3[0], df3[1], 'o', mfc="None")
#     plt.grid(linestyle=':')
#     plt.gca().invert_xaxis()
#     plt.xlabel('Binding energy (eV)')
#     plt.ylabel('Intensity (arb. units)')
#     # plt.legend(fontsize=16)
#     plt.tight_layout()
#     plt.savefig(pngfile, transparent=True, dpi=100)
#     plt.clf()
#     plt.close()
    
    fig, ax = init_figure()
    ax.plot(df3[0], df3[1], 'o', mfc="None")
    ax.invert_xaxis()
    if ylim is not None:
        ax.set_ylim(ylim)
    ax.set_xlabel('Binding energy (eV)')
    ax.set_ylabel('Intensity')
    # ax.legend(fontsize=16)
    fig.tight_layout()
    fig.savefig(pngfile, transparent=False, dpi=100)
    plt.close()
    
    return

def myplot_simple(x, y, xlab, ylab, pngfile, legends = '', logx = False, logy = False, paper = False):
    #PNGファイル出力
    print("Output to", pngfile)
    
    plt.rcParams['font.size'] = 18
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    fig, ax = plt.subplots(1, 1, figsize=(8,6))

    style = ['o', 'D', '^', 'v', 's', '*', '<', '>']
    

#    if setColor:
#        #colList = cm.hsv(np.arange(len(x))/len(x))
#        clist = np.arange(0, len(x))/len(x)
#        for i in range(len(y)):
#            plt.scatter(x, y[i], label = legends[i], vmin=0, vmax=1, c=clist, cmap=cm.hsv)
    for i in range(len(y)):
        if not legends == '':
            ax.plot(x, y[i], style[i], mfc="None", label = legends[i])
        else:
            ax.plot(x, y[i], style[i], mfc="None")

    if paper:
        if (ylab == "AIC") or (ylab == "BIC"):
            idm = y[0].idxmin()
            print(f"idm = {idm}")
            ax.plot(x[idm], y[0][idm], "ro", mfc="None", ms=15, label='_nolegend_')

    if xlab in ['Smoothing number', 'Number of peaks']:
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.tick_params(axis='x', which='minor', bottom=True)
    if ylab in ['Number of peaks']:
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.tick_params(axis='y', which='minor', left=True)
        
    # plt.xlim(x.min(), x.max())
    ax.grid(linestyle=':')
    # plt.gca().invert_xaxis()
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    if logx: ax.set_xscale("log")
    if logy: ax.set_yscale("log")
    if not legends == '':
        ax.legend(fontsize=16)
    fig.tight_layout()
    fig.savefig(pngfile, transparent=False, dpi=100)
    
    if paper:
        # figdpi = 1000
        figfile2 = pngfile.replace(".png", ".tif")
        savefig_by_PIL(fig, figfile2, figdpi=1000)
        # print(f"Output to {figfile2}, dpi = {figdpi}")
        # png1 = BytesIO()
        # fig.savefig(png1, format="png", dpi=figdpi)

        # png2 = Image.open(png1)
        # png2.save(figfile2, compression="tiff_deflate")
        # png1.close()
    
    plt.clf()
    plt.close()
    return

def myplot_auto_smoothing(csvfile):
    # path = './'+dir+'/'+dir+'.csv'
    path = csvfile
    if not os.path.exists(path):
        print('Warning:', path, 'is not exists')
        return
    print('Read data from ', path)
    # pngfile = os.path.basename(path)+'.png'
    # print(pngfile)

    df2 = pd.read_csv(path)
    # print(df2)
    # print(df2.columns)

    # 極端な値を消す

    myplot_simple(df2[df2.columns[0]], [df2[df2.columns[1]]], 'Smoothing points', 'Number of peaks', 'as_NumPeaks.png')
    myplot_simple(df2[df2.columns[0]], [df2[df2.columns[3]]], 'Smoothing points', 'chi^2', 'as_chi2.png', logy = True)
    myplot_simple(df2[df2.columns[0]], [df2[df2.columns[4]]], 'Smoothing points', 'Reduced chi^2', 'as_chi2_reduced.png', logy = True)

    yList = [df2[df2.columns[5]], df2[df2.columns[6]], df2[df2.columns[7]], df2[df2.columns[8]]]
    legendList = ['AIC(Poisson)', 'BIC(Poisson)', 'AIC(Gauss)', 'BIC(Gauss)']
    myplot_simple(df2[df2.columns[0]], yList, 'Smoothing points', 'AIC, BIC', 'as_aic_bic.png', legends = legendList)
    myplot_simple(df2[df2.columns[1]], yList, 'Number of peaks', 'AIC, BIC', 'as_aic_bic_vs_NumPeak.png', legends = legendList)

    yList = [df2[df2.columns[12]], df2[df2.columns[13]]]
    legendList = ['cAIC(Poisson)', 'cAIC(Gauss)']
    myplot_simple(df2[df2.columns[0]], yList, 'Smoothing points', 'cAIC', 'as_cAIC.png', legends = legendList)
    myplot_simple(df2[df2.columns[1]], yList, 'Number of peaks', 'cAIC', 'as_cAIC_vs_NumPeak.png', legends = legendList)

    myplot_simple(df2[df2.columns[0]], [df2[df2.columns[9]]], 'Smoothing points', 'Minimum peak HWHM (eV)', 'as_MinWidth.png')
    # myplot_simple(df2[df2.columns[0]], [df2[df2.columns[10]]], 'Smoothing points', 'Maximum peak HWHM (eV)', 'as_MaxWidth.png')

    myplot_simple(df2[df2.columns[1]], [df2[df2.columns[3]]], 'Number of peaks', 'chi^2', 'as_chi2_vs_NumPeak.png', logy = True)
    myplot_simple(df2[df2.columns[1]], [df2[df2.columns[4]]], 'Number of peaks', 'Reduced chi^2', 'as_chi2_reduced_vs_NumPeak.png', logy = True)

    myplot_simple(df2[df2.columns[1]], [df2[df2.columns[11]]], 'Number of peaks', 'Scaling factor', 'as_chi2_scalingfactor_vs_NumPeak.png')

    return

def myplot_auto_smoothing_minpoints(csvfile):
    # path = './'+dir+'/'+dir+'.csv'
    path = csvfile
    if not os.path.exists(path):
        print('Warning:', path, 'is not exists')
        return

    print('Read data from ', path)
    df2 = pd.read_csv(path)

    myplot_simple(df2[df2.columns[0]], [df2[df2.columns[1]]], 'Smoothing points', 'Minimum points position (eV)', 'as_minpoints.png')
    return

# get_prefered_result(df2, df4, "aic_gauss", "AIC(Gauss)")
def get_prefered_result(df2, df4, key1, key2):
    m = df2[key1].idxmin()
    m_SG = int(df2["smoothing_point"][m])
    method = df2["method"][m]
    
    # series = pd.Series([key2, df2["smoothing_point"][m], df2["numPeak"][m], df2[key1][m]], index=df4.columns)
    series = pd.Series([key2, method, m_SG, df2["numPeak"][m], df2[key1][m]], index=df4.columns)
    df4 = pd.concat([df4, series.to_frame().T], ignore_index=True)  # org: df4 = df4.append(series, ignore_index = True)

#     fname1 = "./result_peak_search_mSG%04d.png" % m_SG
#     fname2 = "./prefered_result_by_%s_mSG%04d_numPeak%s.png" % (key2, m_SG, df2["numPeak"][m])
    fname1 = f"./{method}/result_peak_search_mSG{m_SG:04d}.png"
    fname2 = f'./prefered_result_by_{key2}_{method}_mSG{m_SG:04d}_numPeak{df2["numPeak"][m]}.png'
    # print("HS20180703", key1, key2, fname1, fname2)
    if os.path.exists(fname1):
        print("Copy from %s to %s" % (fname1, fname2))
        shutil.copy2(fname1, fname2)
    else:
        print("Not found %s" % fname1)
    return df4


def myplot_aic_bic(idHigherS, idLowerS, paper=False, figLevel=2):

#     df2 = pd.DataFrame(index=[], columns=["smoothing_point", "numData", "numPeak", "numParam", "variance_gauss", "deviance_gauss", "aic_gauss", "bic_gauss", "deviance_poisson", "aic_poisson", "bic_poisson", "scaling_pgauss", "deviance_pgauss", "aic_pgauss", "bic_pgauss", "chi2", "reduced_chi2", "min_HWHM", "idHigher", "idLower", "energyHigher", "energyLower", "idHigherOrg", "idLowerOrg", "energyHigherOrg", "energyLowerOrg"])
    df2 = pd.DataFrame(index=[], columns=["method", "smoothing_point", "numData", "numPeak", "numParam", "variance_gauss", "deviance_gauss", "aic_gauss", "bic_gauss", "deviance_poisson", "aic_poisson", "bic_poisson", "scaling_pgauss", "deviance_pgauss", "aic_pgauss", "bic_pgauss", "chi2", "reduced_chi2", "min_HWHM", "idHigher", "idLower", "energyHigher", "energyLower", "idHigherOrg", "idLowerOrg", "energyHigherOrg", "energyLowerOrg"])

    for fitting_result_file in glob("./*/result_peak_search_mSG*.csv"):
        
        fitting_parameter_file = fitting_result_file.replace("result", "parameters")
        match = re.search(r'mSG(.*).csv', fitting_result_file)
        i = np.NaN if match is None else match.groups()[0]
        
        match = re.search(r'./(.*)/result_*', fitting_result_file)
        method = np.NaN if match is None else match.groups()[0]

        if not (os.path.exists(fitting_result_file) and os.path.exists(fitting_parameter_file)):
            continue
        # print(fitting_result_file, fitting_parameter_file)
        result = calc_AIC_BIC(fitting_result_file, fitting_parameter_file, idHigherS, idLowerS)

        if result is None:
            continue

#         result[0:0] = [i]
        result[0:0] = [method, i]

        series = pd.Series(result, index=df2.columns)
        df2 = pd.concat([df2, series.to_frame().T], ignore_index=True)  # org: df2 = df2.append(series, ignore_index = True)

    if(len(df2)==0):
        print("Not found any result (1)")
        return

    # 一部の列を型変換
    # df2 = df2.astype({"smoothing_point":"int64", "numData":"int64", "numPeak":"int64", "numParam":"int64"})
    df2 = df2.astype({"smoothing_point":"int64", "numData":"int64", "numPeak":"int64", "numParam":"int64", "idHigher":"int64", "idLower":"int64"})

    # print(df2)
    df2.to_csv("./summary_evalFunc_vs_mSG.csv")

    # 最小のピーク半値半幅が0.1eVより大きいものだけを選ぶ
    df2 = df2[df2.min_HWHM > 0.1]
    # print(df2)

    if(len(df2)==0):
        print("Not found any result (2)")
        return


    # 評価関数を最小にするようなスムージング点数
    df4 = pd.DataFrame(index=[], columns=["function_to_be_minimize", "method", "m_SG", "numPeak", "value"])

    df4 = get_prefered_result(df2, df4, "aic_gauss", "AIC(Gauss)")
    df4 = get_prefered_result(df2, df4, "bic_gauss", "BIC(Gauss)")
    df4 = get_prefered_result(df2, df4, "aic_poisson", "AIC(Poisson)")
    df4 = get_prefered_result(df2, df4, "bic_poisson", "BIC(Poisson)")
    df4 = get_prefered_result(df2, df4, "aic_pgauss", "AIC(Poisson_Gauss)")
    df4 = get_prefered_result(df2, df4, "bic_pgauss", "BIC(Poisson_Gauss)")
    df4 = get_prefered_result(df2, df4, "chi2", "chi^2")
    df4 = get_prefered_result(df2, df4, "reduced_chi2", "reduced_chi2")

    print(df4)
    df4.to_csv("./summary_evalFunc_minvalue.csv")

    if figLevel <= 1:
        return

    # 各種プロット
    myplot_simple(df2["smoothing_point"], [df2["numPeak"]], 'Smoothing number', 'Number of peaks', 'py_NumPeaks.png')
    # myplot_simple(df2["smoothing_point"], [df2["chi2"]], 'Smoothing points', 'chi^2', 'py_chi2.png', logy = True)
    # myplot_simple(df2["smoothing_point"], [df2["reduced_chi2"]], 'Smoothing points', 'Reduced chi^2', 'py_chi2_reduced.png', logy = True)

    # yList = [df2["aic_poisson"], df2["bic_poisson"], df2["aic_gauss"], df2["bic_gauss"]]
    # legendList = ['AIC(Poisson)', 'BIC(Poisson)', 'AIC(Gauss)', 'BIC(Gauss)']
    # myplot_simple(df2["smoothing_point"], yList, 'Smoothing number', 'AIC, BIC', 'py_aic_bic.png', legends = legendList)
    # myplot_simple(df2["numPeak"], yList, 'Number of peaks', 'AIC, BIC', 'py_aic_bic_vs_NumPeak.png', legends = legendList)

    # yList = [df2["aic_poisson"], df2["bic_poisson"]]
    # legendList = ['AIC(Poisson)', 'BIC(Poisson)']
    # myplot_simple(df2["numPeak"], yList, 'Number of peaks', 'AIC, BIC', 'py_aic_poisson_vs_NumPeak.png', legends = legendList)
    #
    # yList = [df2["aic_gauss"], df2["bic_gauss"]]
    # legendList = ['AIC(Gauss)', 'BIC(Gauss)']
    # myplot_simple(df2["numPeak"], yList, 'Number of peaks', 'AIC, BIC', 'py_aic_gauss_vs_NumPeak.png', legends = legendList)

    #shinotsuka20180718
    #AICとBICを分けてプロット
    myplot_simple(df2["numPeak"], [df2["aic_gauss"]], 'Number of peaks', 'AIC', 'py_AIC(Gauss)_vs_NumPeak.png', legends = ['AIC(Gauss)'], paper=paper)
    myplot_simple(df2["numPeak"], [df2["bic_gauss"]], 'Number of peaks', 'BIC', 'py_BIC(Gauss)_vs_NumPeak.png', legends = ['BIC(Gauss)'], paper=paper)
    myplot_simple(df2["numPeak"], [df2["aic_poisson"]], 'Number of peaks', 'AIC', 'py_AIC(Poisson)_vs_NumPeak.png', legends = ['AIC(Poisson)'])
    myplot_simple(df2["numPeak"], [df2["bic_poisson"]], 'Number of peaks', 'BIC', 'py_BIC(Poisson)_vs_NumPeak.png', legends = ['BIC(Poisson)'])

    #shinotsuka20181127
    myplot_simple(df2["numPeak"], [df2["aic_pgauss"]], 'Number of peaks', 'AIC', 'py_AIC(Poisson_Gauss)_vs_NumPeak.png', legends = ['AIC(Poisson_Gauss)'])
    myplot_simple(df2["numPeak"], [df2["bic_pgauss"]], 'Number of peaks', 'BIC', 'py_BIC(Poisson_Gauss)_vs_NumPeak.png', legends = ['BIC(Poisson_Gauss)'])


    #shinotsuka20180718, devianceをプロット
    myplot_simple(df2["numPeak"], [df2["deviance_gauss"]], 'Number of peaks', 'Deviance $D=-2log(L)$', 'py_Deviance(Gauss)_vs_NumPeak.png', legends = ['Deviance(Gauss)'])

    # yList = [df2[df2.columns[12]], df2[df2.columns[13]]]
    # legendList = ['cAIC(Poisson)', 'cAIC(Gauss)']
    # myplot_simple(df2["smoothing_point"], yList, 'Smoothing points', 'cAIC', 'py_cAIC.png', legends = legendList)
    # myplot_simple(df2["numPeak"], yList, 'Number of peaks', 'cAIC', 'py_cAIC_vs_NumPeak.png', legends = legendList)

    myplot_simple(df2["numPeak"], [df2["chi2"]], 'Number of peaks', 'chi^2', 'py_chi2_vs_NumPeak.png', logy = False)
    myplot_simple(df2["numPeak"], [df2["reduced_chi2"]], 'Number of peaks', 'Reduced chi^2', 'py_chi2_reduced_vs_NumPeak.png', logy = False)

    # myplot_simple(df2["numPeak"], [df2["hoge"]], 'Number of peaks', 'Scaling factor', 'py_chi2_scalingfactor_vs_NumPeak.png')
    
    yList = [df2["energyHigherOrg"], df2["energyLowerOrg"]]
    legendList = ['energyHigherOrg', 'energyLowerOrg']
    myplot_simple(df2["smoothing_point"], yList, 'Smoothing number', 'Energy range (eV)', 'py_energyRange.png', legends = legendList)


def getHigherAndLower(fitting_result_file):
    # idHigher, idLower を読み込み、データ数を取得

    # mycmd = 'grep "# idHigher" %s | cut -d" " -f4' % (fitting_result_file)
    # idHigher = subprocess.call(mycmd, shell=True)
    # mycmd = 'grep "# idLower" %s | cut -d" " -f4' % (fitting_result_file)
    # idLower = subprocess.call(mycmd, shell=True)

    ld = open(fitting_result_file)
    lines = ld.readlines()
    ld.close()

    idHigher = ""
    idLower = ""

    for line in lines:
        if line.find("# idHigher") >= 0:
            idHigher= line.split('=')[1].strip()
        if line.find("# idLower") >= 0:
            idLower= line.split('=')[1].strip()
        if(idHigher!="" and idLower!=""):
            break
    # print("idHigher=%s"%idHigher)
    # print("idLower=%s"%idLower)

    return idHigher, idLower


def getEnergyRange():
    idHigherList = []
    idLowerList = []

    # 全部取得する
    for fitting_result_file in glob("./*/result_peak_search_mSG*.csv"):
        if not (os.path.exists(fitting_result_file)):
            continue
        idHigher, idLower = getHigherAndLower(fitting_result_file)
        idHigherList.append(int(idHigher))
        idLowerList.append(int(idLower))
       
    # 指定した範囲から取得する
#     for i in np.arange(1, maxSmoothing+1, 1):
#         fitting_result_file = './result_peak_search_mSG%03d.csv' % i
#         if not (os.path.exists(fitting_result_file)):
#             continue
#         idHigher, idLower = getHigherAndLower(fitting_result_file)
#         idHigherList.append(int(idHigher))
#         idLowerList.append(int(idLower))
#         # print(fitting_result_file, idHigher, idLower)
        
    if(len(idHigherList)):
        idHigherS = min(idHigherList)
    else:
        idHigherS = -1
    if(len(idLowerList)):
        idLowerS = max(idLowerList)
    else:
        idLowerS = -1
    # print(idHigherS, idLowerS)
    return idHigherS, idLowerS

def plot_hist_rmspe(targetDir = "."):
    csvfile = f"{targetDir}/out_rmspeSmoothedSpectrum.csv"
    df1 = pd.read_csv(csvfile, comment="#")
    #ylim=(df1['RMSE'].min(), df1['RMSE'].max())
    ylim=(0.0, df1['RMSPE'].max())
    print(ylim)
    
    fig, axes = init_figure(1, 2, figsize=(12,6))
    axes[0].plot(df1['mSG'], df1['RMSPE'], 'o')
    axes[0].ticklabel_format(style="plain", axis="y")
    axes[0].set_ylim(ylim)
    axes[0].set_xlabel("Number of smoothing")
    axes[0].set_ylabel("NRMSE")


    axes[1].hist(df1['RMSPE'], bins=50, orientation="horizontal")
    ax2 = axes[1].twiny() # another y-axis
    ax2.hist(df1['RMSPE'], bins=50, cumulative=True, density=True, histtype='step', ec='red', orientation="horizontal") # cumulative
    axes[1].ticklabel_format(style="plain", axis="y")
    axes[1].set_ylim(ylim)
    axes[1].set_xlabel("Frequency")
    ax2.set_xlabel("Cummulative frequency")
    axes[1].tick_params(labelleft=False)
    fig.tight_layout()
    
    pngfile= csvfile.replace(".csv", ".png")
    fig.savefig(pngfile, dpi=100)
    return

def plot2Dhist_core(x, y, xlabel='Number of peaks', ylabel='BIC', bins=None, range=None, cmap='rainbow', cmin=1):
    fig, ax = init_figure()

    # H = ax.hist2d(x,y, bins=[binsX,binsY], range=[rangeX, rangeY], cmap='Blues', cmin=1)
    H = ax.hist2d(x,y, bins=bins, range=range, cmap=cmap, cmin=cmin)
    ax.tick_params(axis='x', which='minor', bottom=False)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid()

    # ax.set_title('1st graph')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    H[3].set_clim(0, None)
    fig.colorbar(H[3],ax=ax)
    fig.tight_layout()
    # plt.show()
    # print(H)
    return fig

def plot2Dhist_BIC(targetDir = ".", binsX = None, binsY = 100, rangeX = None, rangeY = None):
    csvfile = f"{targetDir}/summary_evalFunc_vs_mSG.csv"
    print(csvfile)
    df2 = pd.read_csv(csvfile, usecols=['numPeak', 'bic_gauss', 'min_HWHM'])
    df2 = df2[df2.min_HWHM > 0.1]

    x = df2['numPeak']
    y = df2['bic_gauss']
    print("xmin, xmax, ymin, ymax=", x.min(), x.max(), y.min(), y.max())
    
    if binsX is None:
        #binsX = np.arange(0, x.max()+2)
        binsX = np.arange(0.0, x.max()+2, 0.25)    
        
    #binsY = 50
    #rangeX = None
    #rangeY = None
    # rangeX = [1, binsX]
    # rangeY = [950, 1780]
    
    fig = plot2Dhist_core(x, y, bins=[binsX, binsY], range=[rangeX, rangeY], cmap='rainbow', cmin=1)
    
    pngfile = csvfile.replace("summary_evalFunc_vs_mSG.csv", "BIC_vs_NumPeak_hist2D.png")
    print(f"Output to {pngfile}")
    fig.savefig(pngfile, dpi=100)
    return

def plot_result_core(csvfile, idHigherS, idLowerS, paper=False, ylim=None, figLevel=2):
    if figLevel <= 1:
        return
    if not os.path.exists(csvfile):
        print('Warning:', csvfile, 'is not exists')
        return
    # print('Read data from ', csvfile)
    df = pd.read_csv(csvfile, comment='#')

    if idHigherS < 0:
        idHigherS = 0
    if idLowerS < 0:
        idLowerS = len(df) - 1

    peakList = [s for s in df.columns if 'peak[' in s]
    numPeakList = len(peakList)
    # print(numPeakList, peakList)
    if(numPeakList==0):
        print('Warning: %s has no peak', csvfile)
        return

    peakLabel = '%d peaks' % numPeakList if (numPeakList > 1) else '1 peak'

    pngfile = csvfile.replace(".csv", ".png")
    print('Read data from ', csvfile, "  Output to", pngfile)

#    plt.rcParams['figure.figsize'] = (8,6)
    plt.rcParams['font.size'] = 18
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    fig, ax = plt.subplots(1, 1, figsize=(8,6))
    
    ax.plot(df['Binding_Energy(eV)'], df['spectrum'], 'o', mfc='None', ms=5, label="spectrum")
    
    dfc = df[idHigherS:idLowerS+1]
    ax.plot(dfc['Binding_Energy(eV)'], dfc['fitting'], lw=3, label="fitted", alpha=0.8)
    ax.plot(dfc['Binding_Energy(eV)'], dfc[peakList[0]], color="#333333", lw=1, label=peakLabel)
    for c in peakList[1:]:
        ax.plot(dfc['Binding_Energy(eV)'], dfc[c], color="#333333", lw=1, label='_nolegend_')
    ax.plot(dfc['Binding_Energy(eV)'], dfc['background'], label="background")

    if ylim is not None:
        ax.set_ylim(ylim)

    ax.set_xlabel("Binding energy (eV)")
    ax.set_ylabel("Intensity")  ##2021/11/26. cps, count両対応のため単位無しに変更
    ax.invert_xaxis()
    # ax.set_xlim(df['Binding_Energy(eV)'].max(), df['Binding_Energy(eV)'].min())
    ax.grid(ls=":")
    ax.legend(fontsize=14)
    
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style="sci", axis="y",scilimits=(0,0))
    ax.minorticks_on()
    ax.tick_params(axis='both', which='both')
    
    plt.tight_layout()
    fig.savefig(pngfile, transparent=False, dpi=100)
    # plt.savefig("test.svg", transparent=True, dpi=100)
    
    if paper:
        svgfile = pngfile.replace(".png", ".svg")
        print(f"Output to {svgfile}")
        fig.savefig(svgfile, transparent=False, dpi=100)
        
        # figdpi = 1000
        figfile2 = pngfile.replace(".png", ".tif")
        savefig_by_PIL(fig, figfile2, figdpi=1000)
        # print(f"Output to {figfile2}, dpi = {figdpi}")
        # png1 = BytesIO()
        # fig.savefig(png1, format="png", dpi=figdpi)

        # png2 = Image.open(png1)
        # png2.save(figfile2, compression="tiff_deflate")
        # png1.close()
    
    plt.clf()
    plt.close()

def plot_result_wrapper(argsList):
    return plot_result_core(*argsList)

def plot_result(idHigherS, idLowerS, multi=0, globkey="./*/result_peak_search_mSG*.csv", paper=False, ylim=None, figLevel=2):
    csvfileList = glob(globkey)

    #fig, ax = init_figure()
    #plt.close()
    
    if multi==0:
        # シングルプロセスの場合
        for csvfile in csvfileList:
            plot_result_core(csvfile, idHigherS, idLowerS, paper=paper, ylim=ylim, figLevel=figLevel)
    else:
        # 並列処理の場合（複数引数を持つ関数を並列処理するためにラッパー関数をあいだに噛ませる）
        argsList = [ (csvfile, idHigherS, idLowerS, paper, ylim, figLevel) for csvfile in csvfileList ]

        ompnumthreads = os.getenv('OMP_NUM_THREADS')
        print('OMP_NUM_THREADS = ', ompnumthreads)
        if ompnumthreads is None:
            numThreadLimit = 1
        elif not ompnumthreads.isnumeric():
            numThreadLimit = 1
        else:
            numThreadLimit = max(1, int(ompnumthreads))
        print('numThreadLimit = ', numThreadLimit)
        
        p = Pool(numThreadLimit)
        p.map(plot_result_wrapper, argsList)
        p.close()

def parse_args(args):
    input_spectrum_file = ""
    figLevel = 2
    # figflag = True

    for arg in args[1:]:
        if arg == '-nofig':
            # figflag = False
            figLevel = 0
        elif arg == '-minfig':
            figLevel = 1
        elif arg == '-allfig':
            figLevel = 2
        else:
            if os.path.exists(arg):
                input_spectrum_file = arg
            elif os.path.exists(arg + ".csv"):
                input_spectrum_file = arg + ".csv"
            else:
                print("Unrecognized argument: ", arg)
    
    return input_spectrum_file, figLevel

def get_recipeData():
    recipeData = {}
    ## recipe.txtからpptに出力するピーク本数の最大値を取得する
    recipeFile = './recipe.txt'
    if os.path.exists(recipeFile):
        ## Output recipeFile as it is
        with open(recipeFile, 'r') as f:
            print('\nrecipe file = \n--------------------\n' + f.read() + '--------------------\n')
        ## Read recipe file to get options as dict format
        recipeData = {}
        with open(recipeFile, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                recipeData[row[0]] = row[1]
    print('recipeData:'); print(recipeData)
    return recipeData
#

if __name__=='__main__':
    args = sys.argv
    input_spectrum_file, figLevel = parse_args(args)
    print(f"input_spectrum_file = {input_spectrum_file}")
    print(f"figLevel = {figLevel}")

    recipeData = get_recipeData()
    numPeakMax = None
    if 'numPeakMax' in recipeData:
        numPeakMax = int(recipeData['numPeakMax'])

    idHigherS, idLowerS = getEnergyRange()
    
    #print("plot_result() is hidden temporary")
    #plot_result(idHigherS, idLowerS, multi=0)
    
    if figLevel == 2:
        plot_result(idHigherS, idLowerS, multi=1, figLevel=figLevel)

    myplot_aic_bic(idHigherS, idLowerS, figLevel=figLevel)
    
    if figLevel >= 2:
        plot2Dhist_BIC("./")
    
    # get_prefered_result_by_BIC("./", figLevel=figLevel)
    get_prefered_result_by_BIC_groupbypeaks("./", numPeakMax)


    # ## figLevel==1のとき必要最小限のランク１～５だけ図を作る
    # if figLevel == 1:
    #     plot_result(idHigherS, idLowerS, multi=0, globkey="./BIC_rank*_result.csv")

    ## figLevel==1のときピックアップしたランクだけ図を作る
    if figLevel == 1:
        # plot_result(idHigherS, idLowerS, multi=0, globkey="./BIC_rank*_result.csv")
        plot_result(idHigherS, idLowerS, multi=1, globkey="./gbp_rank*_result.csv")

    if figLevel >= 1:
        # 入力スペクトルをプロット
        # plot_input_spectrum(input_spectrum_file)
        p = Process(target=plot_input_spectrum, args=(input_spectrum_file,))
        p.start()
        p.join()

        # smoothed spectrum のRMSPEのヒストグラム
        # plot_hist_rmspe()

        # 無視
        # myplot_auto_smoothing("out_auto_smoothing2.csv")
        # myplot_auto_smoothing_minpoints("out_auto_smoothing_minpoints.csv")

    # np.savetxt('as_plot.done', [])

