import pdfplumber
import os
from model.basic_extract import BasicExtractModel
from model.two_year_extract import TwoYearModel


"""
Testing:
  Valid:
  - 四技
  - 博士班
  - 進四技
  - 碩士班
  - 碩專班
  - 二技
  Invalid:
  - None
"""


def run(pdf, output_dir, FILE_NAME):
    basic = BasicExtractModel(pdf)
    try:
        basic.check_file()
    except Exception as e:
        if e.args[0] != basic.WRONG_FILE:
            raise
        two_year = TwoYearModel(pdf)
        try:
            two_year.check_file()
        except Exception as e:
            if e.args[0] != two_year.WRONG_FILE:
                raise
        else:
            two_year.run_program()
            two_year.save_csv(output_dir, FILE_NAME)
    else:
        basic.run_program()
        basic.save_csv(output_dir, FILE_NAME)


if __name__ == '__main__':
    # FILE_NAMES = ['四技']
    FILE_NAMES = ['四技', '博士班', '進四技', '碩士班', '碩專班', '二技']

    for FILE_NAME in FILE_NAMES:
        PROJECT_PATH = os.path.abspath('./')
        DIR_NAME = 'input(pdf)'
        FILE_EXT = '.pdf'
        PDF_PATH = os.path.join(PROJECT_PATH, DIR_NAME, FILE_NAME + FILE_EXT)

        pdf = pdfplumber.open(PDF_PATH)
        output_dir = os.path.join(PROJECT_PATH, 'output(csv)')
        run(pdf, output_dir, FILE_NAME)
