import pdfplumber
import pandas as pd
import os
import re


class TwoYearModel:
    """
    two-year technical program
    """
    def __init__(self, pdf: pdfplumber.PDF):
        self.pdf = pdf
        self.pdf_cleaned = None
        self.pdf_df = None
        self.WRONG_FILE = 'file is wrong'

    def check_file(self):
        text = self.pdf.pages[0].extract_text()
        check_word = re.search(r'二技課程表', text)
        if check_word is None:
            raise Exception(self.WRONG_FILE)

    def pdf_clean(self):
        def remove_blank(text):
            if text is None:
                return None
            regex_remove_blank = r' '
            return re.sub(regex_remove_blank, '', text)

        def table_clean(table):
            results_table = []
            for row in table:
                temp = map(remove_blank, row)
                results_table.append(list(temp))
            return results_table

        results_pdf = []
        for page in self.pdf.pages:
            buffer_table = page.extract_table()
            if buffer_table is not None:
                buffer_table = table_clean(buffer_table)
                results_pdf.append(buffer_table)
        self.pdf_cleaned = results_pdf

    def make_dataframe(self):
        self.pdf_df = list(map(pd.DataFrame, self.pdf_cleaned))

    def concat_dataframe(self):
        pdf_concat = self.pdf_df[0]
        page_start = 1
        page_end = len(self.pdf_df)
        for page in range(page_start, page_end):
            col_0 = list(self.pdf_df[page].iloc[:, 0])
            flag = None
            for key, value in enumerate(col_0):
                if flag and value is not None:
                    cut_index = key
                    break
                if value == r'年級\n類別':
                    flag = True
            else:
                cut_index = 0

            pdf_concat = pd.concat([pdf_concat, self.pdf_df[page].iloc[cut_index:, :]], axis=0, ignore_index=True)

        self.pdf_df = pdf_concat

    def clean_newline(self):
        def remove_blank(text):
            if text is None:
                return None
            regex_remove_blank = r'\s'
            return re.sub(regex_remove_blank, '', text)

        self.pdf_df.iloc[:, 0] = list(map(remove_blank, list(self.pdf_df.iloc[:, 0])))
        pass

    def clean_subtotal(self):
        def search_keyword(text):
            flag = re.search(r'^小計', str(text))
            if flag is None or flag == False:
                return False
            else:
                return True

        finally_df = self.pdf_df.drop(self.pdf_df[self.pdf_df[0].apply(search_keyword)].index)
        finally_df = finally_df.reset_index(drop=True)
        finally_df = pd.DataFrame(finally_df)
        self.pdf_df = finally_df

    def extract_data(self):
        def get_grade(df, row, col):
            target_row = 0
            target_col = col
            df = pd.DataFrame(df)
            grade = df.iloc[target_row, target_col]
            while grade is None or grade == "":
                target_col -= 1
                grade = df.iloc[target_row, target_col]
            return grade

        def get_term(df, row, col):
            target_row = 1
            target_col = col
            df = pd.DataFrame(df)
            term = df.iloc[target_row, target_col]
            while term is None or term == "":
                target_col -= 1
                term = df.iloc[target_row, target_col]
            return term

        def get_cls(df, row, col):
            target_row = row
            target_col = 0
            df = pd.DataFrame(df)
            cls = df.iloc[target_row, target_col]
            while cls is None or cls == "":
                target_row -= 1
                cls = df.iloc[target_row, target_col]
            return cls

        def get_category(df, row, col):
            target_row = row
            target_col = 1
            df = pd.DataFrame(df)
            category = df.iloc[target_row, target_col]
            while category is None or category == "":
                target_row -= 1
                category = df.iloc[target_row, target_col]
            return category

        row_start = self.pdf_df[self.pdf_df[0].isin(['專業必修科目'])].index[0]
        row_end = self.pdf_df.shape[0]
        col_start = self.pdf_df.loc[:, self.pdf_df.iloc[0, :].isin(['第一學年'])].columns[0]
        col_end = self.pdf_df.shape[1] - 1

        course_info = []
        for row in range(row_start, row_end):
            for col in range(col_start, col_end, 2):
                buffer = []
                buffer.append(get_cls(self.pdf_df, row, col))  # 課程類別
                buffer.append(get_category(self.pdf_df, row, col))  # 領域類別
                buffer.append(get_grade(self.pdf_df, row, col))  # 年級
                buffer.append(get_term(self.pdf_df, row, col))  # 學期
                buffer.append(self.pdf_df.iloc[row, col])  # 課程
                buffer.append(self.pdf_df.iloc[row, col + 1])  # 學分
                # buffer.append(self.pdf_df.iloc[row, col + 2])  # 時數

                course_info.append(buffer)

        course_df = pd.DataFrame(course_info)
        course_df.columns = ['課程類別', '領域類別', '年級', '學期', '課程', '學分/時數']
        self.pdf_df = course_df

    def split_course(self):
        end = self.pdf_df.shape[0]
        course_info = []
        for row in range(end):
            course_list = str(self.pdf_df['課程'][row]).split('\n')
            term_time_list = str(self.pdf_df['學分/時數'][row]).split('\n')
            for key, course in enumerate(course_list):
                buffer = []
                buffer.append(self.pdf_df['課程類別'][row])
                buffer.append(self.pdf_df['領域類別'][row])
                buffer.append(self.pdf_df['年級'][row])
                buffer.append(self.pdf_df['學期'][row])
                try:
                    term_time = term_time_list[key]
                except IndexError:
                    term_time = None
                if term_time is not None and term_time != 'None' and term_time != '':
                    term_time_split = term_time.split('/')
                    buffer.append(course)
                    buffer.append(term_time_split[0])
                    buffer.append(term_time_split[1])
                else:
                    regex_results = re.search(r'(\d/\d)$', course)
                    if regex_results is not None:
                        buffer.append(course[0: regex_results.start()])
                        term_time = regex_results.group()
                        if term_time is not None and term_time != 'None' and term_time != '':
                            term_time_split = term_time.split('/')
                            buffer.append(term_time_split[0])
                            buffer.append(term_time_split[1])
                        else:
                            buffer.append(None)
                            buffer.append(None)
                    else:
                        buffer.append(course)
                        buffer.append(None)
                        buffer.append(None)

                course_info.append(buffer)
        course_df = pd.DataFrame(course_info)
        course_df.columns = ['課程類別', '領域類別', '年級', '學期', '課程', '學分', '時數']
        self.pdf_df = course_df

    def clean_data(self):
        finally_df = self.pdf_df.drop(self.pdf_df[self.pdf_df['課程'].isin(['', 'None', None])].index)
        finally_df = finally_df.reset_index(drop=True)
        finally_df = pd.DataFrame(finally_df)
        self.pdf_df = finally_df

    def save_csv(self, output_dir, filename: str):
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        output_filename = f'extract - {filename}.csv'
        output = os.path.join(output_dir, output_filename)
        self.pdf_df.to_csv(output, encoding='utf-8-sig', index=False)

    def get_df(self):
        return self.pdf_df

    def run_program(self):
        self.pdf_clean()
        self.make_dataframe()
        self.concat_dataframe()
        self.clean_newline()
        self.clean_subtotal()
        self.extract_data()
        self.split_course()
        self.clean_data()
