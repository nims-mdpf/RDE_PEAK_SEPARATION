import os
# import sys
import subprocess as sp
import argparse
# import time
# from glob import glob

# import numpy as np
# import pandas as pd
import time
import datetime
import csv

PYTHON = "python3"
toolname = "xps-ps-cv-20240712"
bindir = os.path.abspath(os.path.dirname(__file__))
PY_FLOW = f"{bindir}/flow.py"


def set_recipe_data(noise: str):
    recipe_data = {"bg": "", "noise": "-g", "pptx": "-x", "optmode": "simple", "dev": ""}

    recipe_file = "recipe.txt"

    if os.path.exists(recipe_file):
        # Output recipe_file as it is
        with open(recipe_file, "r") as f:
            print("\nrecipe file = \n--------------------\n" + f.read() + "--------------------\n")

        # Read recipe file to get background option and noise option as dict format
        with open(recipe_file, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                row[0] = row[0].lower()
                row[1] = row[1].lower()
                if row[0] == "bg":
                    if row[1] in ["shirley"]:
                        recipe_data["bg"] = "-s"
                    elif row[1] in ["linear"]:
                        recipe_data["bg"] = "-l"
                if row[0] == "noise":
                    if row[1] in ["gauss"]:
                        recipe_data["noise"] = "-g"
                    elif row[1] in ["poisson"]:
                        recipe_data["noise"] = "-p"
                if row[0] == "pptx":
                    if row[1] in ["1"]:
                        recipe_data["pptx"] = "-x"
                    elif row[1] in ["0"]:
                        recipe_data["pptx"] = ""
                if row[0] == "dev":
                    if row[1] in ["1"]:
                        recipe_data["dev"] = "-d"
                if row[0] == "optmode":
                    if row[1] in ["full"]:
                        recipe_data["optmode"] = "--full"
    else:
        if noise == "gauss":
            recipe_data["noise"] = "-g"
        else:
            recipe_data["noise"] = "-p"        
        print(f"{recipe_file} not found. Set default recipe_data and invoice setting.")

    return recipe_data


if __name__ == "__main__":

    print(f"# Tool name = {toolname}")
    print(f"# Start time = {datetime.datetime.now()}")
    startTimeTmp = time.time()  # start time
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path")
    parser.add_argument("--noise", help="noise type", default="gauss", choices=['gauss', 'poisson'])
    options = parser.parse_args()
    spectrumfile = options.file_path
    noise = options.noise
#    print(sys.argv)

#    if len(sys.argv) != 2:
#        print(f"Error! Usage: {sys.argv[0]} <spectrum data file>")
#        sys.exit(1)

#    spectrumfile = sys.argv[1]

    recipe_data = set_recipe_data(noise)

    print("recipe_data = ", recipe_data)

    cmd = [PYTHON, PY_FLOW, spectrumfile, recipe_data["bg"], recipe_data["noise"], recipe_data["pptx"], recipe_data["optmode"], recipe_data["dev"]]
    print(cmd, flush=True)

    status = sp.run(cmd)
    print(status)

    print(f"# End time = {datetime.datetime.now()}")
    td = time.time() - startTimeTmp
    print(toolname + " run time is %.2f (sec) =  %s" % (td, datetime.timedelta(seconds=td)))
