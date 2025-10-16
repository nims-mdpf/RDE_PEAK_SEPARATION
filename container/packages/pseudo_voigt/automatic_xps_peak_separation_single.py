#!/usr/bin/env python3
# coding: utf-8

import csv
import pandas as pd
import sys, os, subprocess
from glob import glob
import shutil

## Specify the directory which has "activeshirley_gcc.exe" and "plot_result.py"
#software_dir = "/mnt/c/Users/shinotsuka/Documents/1_ActiveShirley/ActiveShirley_on_server/20190704_shinotsuka"
software_dir = os.path.abspath(os.path.dirname(__file__))
activeshirley_exe_file = f"{software_dir}/activeshirley_gcc.exe"
plot_py_file = f"{software_dir}/plot_result_shirley_and_linear.py"
settingsShirleyBG = f"{software_dir}/settings_Shirley.inp"
settingsLinearBG = f"{software_dir}/settings_Linear.inp"
ppt_py_file = f"{software_dir}/make_result_figures_ppt2.py"
# PYTHON = "python3.7"
PYTHON = "python3"
toolname = 'xps-ps-pv-20220419'

print(f'# toolname               = {toolname}')
print(f"# software_dir             = {software_dir}")
print(f"# activeshirley_exe_file   = {activeshirley_exe_file}")
print(f"# plot_py_file             = {plot_py_file}")
print(f"# ppt_py_file              = {ppt_py_file}")

def exec_command(cmd, targetdir="./", logfile=""):
    """
    Execute a command cmd assuming a Linux system.
    If specified, stdout and stderr will be output to logfile.
    Otherwise, the log is output to the standard console.
    
    >>> exec_command('echo hello')
    0
    """
    if logfile == "":
        p = subprocess.Popen(cmd, cwd = targetdir, shell=True)
    else:
        p = subprocess.Popen(cmd.split(), cwd = targetdir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        with open(logfile, mode='w') as f:
            for l in p.stdout:
                l = l.decode('utf-8').rstrip()
                f.write(l + '\n')
                #print(l)
    p.wait()
    return p.returncode
#
def get_num_model(kwd):
    ## 最小のピーク半値半幅が0.1eVより大きいモデルの個数を返す
    numModel = 0
    paramfileList = list(glob(f"./{kwd}/parameters_peak_search_mSG*.csv"))
    for paramfile in paramfileList:
        dfp = pd.read_csv(paramfile, usecols=['width'])
        min_HWHM = dfp.width[dfp.width.idxmin()]
        if min_HWHM > 0.1:
            numModel = numModel + 1
    return numModel

def main_core(fnm, kwd, devFlag = False):
    pwd = os.getcwd()

    ## kwdはshirleyまたはlinear
    ## kwdディレクトリを作る
    targetdir = kwd
    os.makedirs(targetdir, exist_ok=True)

    ## スペクトルデータファイルをコピーする
    shutil.copy2(fnm, targetdir)

    ## settingsShirleyBG.inp または settingsLinearBG.inp を settings.inp と名前を変えてそのディレクトリにコピーする
    if kwd == "shirley":
        settingsfile = settingsShirleyBG
    elif kwd == "linear":
        settingsfile = settingsLinearBG
    else:
        print("kwd must be shirley or linear")
        sys.exit(1)

    if os.path.exists(settingsfile):
        shutil.copy2(settingsfile, f"{targetdir}/settings.inp")

    ## 自動ピーク分離を実行し，標準出力をlog1.txtに書き出す
    cmd = f'{activeshirley_exe_file} {fnm}' 
    print(cmd)
    exec_command(cmd, targetdir, f'log_as_{kwd}.txt')
    # numfile = len(list(glob(f"./{kwd}/parameters_peak_search_mSG*.csv")))
    numModel = get_num_model(kwd)
    print(f"Number of valid models for {kwd} BG = {numModel}")
    return numModel


def main(fnm, bgType='auto', figType='-minfig', pptFlag=False, devFlag = False):
    
    if (bgType == 'auto'):
        numModel = main_core(fnm, "shirley", devFlag)

        if numModel == 0:
            numModel = main_core(fnm, "linear", devFlag)

    elif (bgType == 'shirley'):
        numModel = main_core(fnm, "shirley", devFlag)
    elif (bgType == 'linear'):
        numModel = main_core(fnm, "linear", devFlag)

    ## 事後処理を実行し，標準出力をlog2.txtに書き出す
    cmd = f'{PYTHON} {plot_py_file} {fnm} {figType}'
    print(cmd)
    exec_command(cmd, logfile='log2.txt')

    if numModel == 0:
        print("Warning. No result found.")
    elif pptFlag:
        ## 結果をpptにまとめる
        cmd = f'{PYTHON} {ppt_py_file}'
        print(cmd)
        exec_command(cmd, logfile='log3.txt')

    ## 無用の中間ファイルを削除
    if not devFlag:
        # cmd = "rm -f out_*.csv parameters_*.csv prefered_*.png py_*.png result_* summary_evalFunc_minvalue.csv summary_evalFunc_vs_mSG.csv"
        cmd = "rm -rf linear shirley prefered_*.png py_*.png summary_evalFunc_minvalue.csv summary_evalFunc_vs_mSG.csv"
        print(cmd)
        exec_command(cmd)
    return
#
if __name__=='__main__':
    args = sys.argv
    # print(args)
    #args = ["./Untitled.py", "MIDATA001.107.csv", "O1s"]
    
    figType = '-minfig'

    ## 引数に '-d' があれば開発者モード．全ての図を作る．中間ファイルを削除せずに残す．
    devFlag = ('-d' in args)
    if devFlag:
        figType = '-allfig'

    ## 引数に '-p' があれば結果をまとめたpptファイルを作る．
    pptFlag = ('-p' in args)

    ## デフォルトではまずShirley法を実施し，モデルが見つからない場合は直線法を実施する
    ## 引数に '-l' があればバックグラウンドを直線法で近似する
    ## 引数に '-s' があればバックグラウンドをShirley法で近似する
    ## 引数に '-nofig' があれば図を作らない．時間短縮用
    ## 引数に '-minfig' があれば必要最小限の図を作る．時間短縮用
    ## 引数に '-allfig' があれば全ての図を作る．
    bgType = 'auto'
    if ('-s' in args):
        bgType = 'shirley'
    elif ('-l' in args):
        bgType = 'linear'
    if ('-nofig' in args):
        figType = '-nofig'
    elif ('-minfig' in args):
        figType = '-minfig'
    elif ('-allfig' in args):
        figType = '-allfig'


    # args = [a for a in args if (a != '-d')]
    args = [a for a in args if (not a.startswith('-'))]
    print(f'bgType = {bgType}, figType = {figType}, devFlag = {devFlag}')
    print(args)
    
    if len(args) <= 1:
        print(f'Usage:\n        {args[0]} <csv file> [-d] [-s|-l] [-p] [-allfig|-minfig|-nofig]')
        print(f'Example:\n        {args[0]} spectrumdata.csv')
        print('        <csv file> is a XPS data file in CSV-format.')
        print('        "-d" for developer mode')
        print('        "-s" for only Shirley background')
        print('        "-l" for only Linear background')
        print('        "-p" creats a summary ppt file')
        print('        "-allfig" will create all figures')
        print('        "-minfig" will create only minimum necessary figures (default)')
        print('        "-nofig" will not create any figures')
        sys.exit(1)
        
    main(args[1], bgType, figType, pptFlag, devFlag)
    
