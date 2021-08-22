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

FILE_NAME = '四技'

PROJECT_PATH = os.path.abspath('./')
DIR_NAME = 'input(pdf)'
FILE_EXT = '.pdf'
PDF_PATH = os.path.join(PROJECT_PATH, DIR_NAME, FILE_NAME + FILE_EXT)


if __name__ == '__main__':
    pdf = pdfplumber.open(PDF_PATH)
    output_dir = os.path.join(PROJECT_PATH, 'output(csv)')
    basic = BasicExtractModel(pdf)
    try:
        basic.check_file()
    except Exception as e:
        two_year = TwoYearModel(pdf)
        try:
            two_year.check_file()
        except Exception as e:
            raise
        two_year.run_program()
        two_year.save_csv(output_dir, FILE_NAME)
    else:
        basic.run_program()
        basic.save_csv(output_dir, FILE_NAME)

    pass
