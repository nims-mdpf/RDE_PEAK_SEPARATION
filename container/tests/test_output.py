import os
import shutil
from typing import Union


def setup_inputdata_folder(inputdata_name: Union[str, list[str]]):
    """テスト用でdataフォルダ群の作成とrawファイルの準備

    Args:
        inputdata_name (Union[str, list[str]]): rawファイル名
    """
    destination_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(destination_path, exist_ok=True)
    os.makedirs(os.path.join(destination_path, "inputdata"), exist_ok=True)
    os.makedirs(os.path.join(destination_path, "invoice"), exist_ok=True)
    inputdata_original_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "inputdata")

    tasksupport_original_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "templates",
        "template",
        "tasksupport",
    )

    if isinstance(inputdata_name, list):
        for item in inputdata_name:
            shutil.copy(
                os.path.join(inputdata_original_path, item),
                os.path.join(destination_path, "inputdata"),
            )
    else:
        shutil.copy(
            os.path.join(inputdata_original_path, inputdata_name),
            os.path.join(destination_path, "inputdata"),
        )
    if not os.path.exists(os.path.join(destination_path, "tasksupport")):
        shutil.copytree(tasksupport_original_path, os.path.join(destination_path, "tasksupport"))


def setup_invoice_file(path: str):
    """テスト用でinvoiceファイルの準備

    Args:
        path (Union[str, list[str]]): rawファイル名
    """
    destination_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(destination_path, exist_ok=True)
    os.makedirs(os.path.join(destination_path, "invoice"), exist_ok=True)
    inputdata_original_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "inputdata")
#   inputdata_original_path = path

    shutil.copy(
        os.path.join(inputdata_original_path, path),
        os.path.join(destination_path, "invoice"),
    )


def setup_file(dirname: str, path: str):
    """Sets up the file structure and copies a specified file to a destination directory.
    This function creates a directory structure under a "data" directory located two levels up from the current file's directory.
    It then copies a file from an "inputdata" directory located three levels up from the current file's directory to the newly created directory.

    Args:
        dirname (str): The name of the subdirectory to create under the "data" directory.
        path (str): The relative path of the file to copy from the "inputdata" directory.

    Raises:
        OSError: If the file or directory operations fail.

    """

    destination_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(destination_path, exist_ok=True)
    os.makedirs(os.path.join(destination_path, dirname), exist_ok=True)
    inputdata_original_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "inputdata")

    shutil.copy(
        os.path.join(inputdata_original_path, path),
        os.path.join(destination_path, dirname),
    )


class TestOutputCase1:
    """case1
    畳み込みVoigt関数を基底関数とした自動ピークフィッティングの入出力テスト
    入力ファイル: input.csv、output.csvの正常系テスト(in「xxx」ファイル、out「xxx」ファイルのインプットデータの定義に沿ったもの)
    """

    # inputdata: Union[str, list[str]] = "<テストで使用する入力ファイルパス: リポジトリ直下inputdataディィレクトリ以下>"
    # invoice: str = "<テストで使用するinvoice.jsonパス: リポジトリ直下inputdataディィレクトリ以下>"
    inputdata: Union[str, list[str]] = ["case1/inputdata/XPS_PMMA_C1s_Al.csv"]
    invoice: str = "case1/invoice/invoice.json"

    def test_setup(self):
        # MEMO: Dockerの外からコピーする為、手動でsetupする。
        # setup_inputdata_folder(self.inputdata)
        # setup_inputdata_folder(self.inputdata)
        # setup_invoice_file(self.invoice)
        ...

    def test_raw_data(self, setup_main, data_path):
        assert os.path.exists(os.path.join(data_path, "nonshared_raw", "XPS_PMMA_C1s_Al.csv"))

    def test_main_image(self, data_path):
        assert os.path.exists(os.path.join(data_path, "main_image", "XPS_PMMA_C1s_Al_summary0001-1.png"))

    def test_other_image(self, data_path):
        assert os.path.exists(os.path.join(data_path, "other_image", "BIC_vs_NumPeak.png"))
        assert os.path.exists(os.path.join(data_path, "other_image", "gbp_rank1_numPeak4_auto_shirley_result.png"))
        assert os.path.exists(os.path.join(data_path, "other_image", "gbp_rank2_numPeak5_auto_shirley_result.png"))
        assert os.path.exists(os.path.join(data_path, "other_image", "gbp_rank3_numPeak7_auto_shirley_result.png"))
        assert os.path.exists(os.path.join(data_path, "other_image", "gbp_rank4_numPeak6_auto_shirley_result.png"))
        assert os.path.exists(os.path.join(data_path, "other_image", "gbp_rank5_numPeak10_auto_shirley_result.png"))
        assert os.path.exists(os.path.join(data_path, "other_image", "gbp_rank6_numPeak9_auto_shirley_result.png"))
        assert os.path.exists(os.path.join(data_path, "other_image", "gbp_rank7_numPeak8_auto_shirley_result.png"))
        assert os.path.exists(os.path.join(data_path, "other_image", "gbp_rank8_numPeak3_auto_shirley_result.png"))
        assert os.path.exists(os.path.join(data_path, "other_image", "gbp_rank9_numPeak2_auto_shirley_result.png"))
        assert os.path.exists(os.path.join(data_path, "other_image", "gbp_rank10_numPeak1_auto_shirley_result.png"))
        assert os.path.exists(os.path.join(data_path, "other_image", "input_spectrum2.png"))
        assert os.path.exists(os.path.join(data_path, "other_image", "XPS_PMMA_C1s_Al_summary0001-2.png"))

    def test_structured(self, data_path):
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank1_numPeak4_auto_shirley_parameters.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank1_numPeak4_auto_shirley_result.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank2_numPeak5_auto_shirley_parameters.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank2_numPeak5_auto_shirley_result.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank3_numPeak7_auto_shirley_parameters.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank3_numPeak7_auto_shirley_result.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank4_numPeak6_auto_shirley_parameters.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank4_numPeak6_auto_shirley_result.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank5_numPeak10_auto_shirley_parameters.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank5_numPeak10_auto_shirley_result.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank6_numPeak9_auto_shirley_parameters.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank6_numPeak9_auto_shirley_result.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank7_numPeak8_auto_shirley_parameters.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank7_numPeak8_auto_shirley_result.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank8_numPeak3_auto_shirley_parameters.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank8_numPeak3_auto_shirley_result.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank9_numPeak2_auto_shirley_parameters.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank9_numPeak2_auto_shirley_result.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank10_numPeak1_auto_shirley_parameters.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank10_numPeak1_auto_shirley_result.csv"))
        assert os.path.exists(os.path.join(data_path, "structured", "result_figures.pptx"))
        assert os.path.exists(os.path.join(data_path, "structured", "summary_BIC.csv"))

    def test_thumbnail(self, data_path):
        assert os.path.exists(os.path.join(data_path, "thumbnail", "XPS_PMMA_C1s_Al_summary0001-1.png"))


# class TestOutputCase2:
#     """case2
#     疑似Voigt関数を基底関数とした自動ピークフィッティングの入出力テスト
#     入力ファイル: input.csv、output.csvの正常系テスト(in「xxx」ファイル、out「xxx」ファイルのインプットデータの定義に沿ったもの)
#     """

#     # inputdata: Union[str, list[str]] = "<テストで使用する入力ファイルパス: リポジトリ直下inputdataディィレクトリ以下>"
#     # invoice: str = "<テストで使用するinvoice.jsonパス: リポジトリ直下inputdataディィレクトリ以下>"
#     inputdata: Union[str, list[str]] = ["case2/inputdata/XPS_PMMA_C1s_Al.csv"]
#     invoice: str = "case2/invoice/invoice.json"

#     def test_setup(self):
#         # MEMO: Dockerの外からコピーする為、手動でsetupする。
#         # setup_inputdata_folder(self.inputdata)
#         # setup_inputdata_folder(self.inputdata)
#         # setup_invoice_file(self.invoice)
#         ...

#     def test_raw_data(self, setup_main, data_path):
#         assert os.path.exists(os.path.join(data_path, "nonshared_raw", "XPS_PMMA_C1s_Al.csv"))

#     def test_main_image(self, data_path):
#         assert os.path.exists(os.path.join(data_path, "main_image", "XPS_PMMA_C1s_Al_summary0001-1.png"))

#     def test_other_image(self, data_path):
#         assert os.path.exists(os.path.join(data_path, "other_image", "BIC_vs_NumPeak.png"))
#         assert os.path.exists(os.path.join(data_path, "other_image", "gbp_rank1_numPeak4_shirley_mSG0704_result.png"))
#         assert os.path.exists(os.path.join(data_path, "other_image", "gbp_rank2_numPeak5_shirley_mSG0672_result.png"))
#         assert os.path.exists(os.path.join(data_path, "other_image", "gbp_rank3_numPeak7_shirley_mSG0304_result.png"))
#         assert os.path.exists(os.path.join(data_path, "other_image", "gbp_rank4_numPeak6_shirley_mSG0528_result.png"))
#         assert os.path.exists(os.path.join(data_path, "other_image", "gbp_rank5_numPeak10_shirley_mSG0232_result.png"))
#         assert os.path.exists(os.path.join(data_path, "other_image", "gbp_rank6_numPeak3_shirley_mSG1568_result.png"))
#         assert os.path.exists(os.path.join(data_path, "other_image", "gbp_rank7_numPeak2_shirley_mSG2624_result.png"))
#         assert os.path.exists(os.path.join(data_path, "other_image", "input_spectrum2.png"))
#         assert os.path.exists(os.path.join(data_path, "other_image", "XPS_PMMA_C1s_Al_summary0001-2.png"))

#     def test_structured(self, data_path):
#         assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank1_numPeak4_shirley_mSG0704_parameters.csv"))
#         assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank1_numPeak4_shirley_mSG0704_result.csv"))
#         assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank2_numPeak5_shirley_mSG0672_parameters.csv"))
#         assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank2_numPeak5_shirley_mSG0672_result.csv"))
#         assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank3_numPeak7_shirley_mSG0304_parameters.csv"))
#         assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank3_numPeak7_shirley_mSG0304_result.csv"))
#         assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank4_numPeak6_shirley_mSG0528_parameters.csv"))
#         assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank4_numPeak6_shirley_mSG0528_result.csv"))
#         assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank5_numPeak10_shirley_mSG0232_parameters.csv"))
#         assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank5_numPeak10_shirley_mSG0232_result.csv"))
#         assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank6_numPeak3_shirley_mSG1568_parameters.csv"))
#         assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank6_numPeak3_shirley_mSG1568_result.csv"))
#         assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank7_numPeak2_shirley_mSG2624_parameters.csv"))
#         assert os.path.exists(os.path.join(data_path, "structured", "gbp_rank7_numPeak2_shirley_mSG2624_result.csv"))
#         assert os.path.exists(os.path.join(data_path, "structured", "result_figures.pptx"))
#         assert os.path.exists(os.path.join(data_path, "structured", "summary_BIC.csv"))

#     def test_thumbnail(self, data_path):
#         assert os.path.exists(os.path.join(data_path, "thumbnail", "XPS_PMMA_C1s_Al_summary0001-1.png"))
