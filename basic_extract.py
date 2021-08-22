import pdfplumber
import pandas as pd
import os
import re


class BasicExtractModel:
    """
    Basic Extract
    """
    def __init__(self, pdf: pdfplumber.PDF):
        self.pdf = pdf
        self.pdf_cleaned = None
        self.pdf_df = None

    def check_file(self):
        text = self.pdf.pages[0].extract_text()
        check_word = re.search(r'課程結構規劃表', text)
        if check_word is None:
            raise Exception('file is wrong')

    def pdf_clean(self):
        def remove_blank(text):
            if text is None:
                return None
            regex_remove_blank = r'\s'
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
                if value == '課程類別':
                    flag = True
            else:
                cut_index = 0

            pdf_concat = pd.concat([pdf_concat, self.pdf_df[page].iloc[cut_index:, :]], axis=0, ignore_index=True)

        self.pdf_df = pdf_concat

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

        def get_type(df, row, col):
            target_row = row
            target_col = 1
            df = pd.DataFrame(df)
            course_type = df.iloc[target_row, target_col]
            while course_type is None or course_type == "":
                target_row -= 1
                course_type = df.iloc[target_row, target_col]
            return course_type

        def get_category(df, row, col):
            target_row = row
            target_col = 2
            df = pd.DataFrame(df)
            category = df.iloc[target_row, target_col]
            while category is None or category == "":
                target_row -= 1
                category = df.iloc[target_row, target_col]
            return category

        row_start = self.pdf_df[self.pdf_df[0].isin(['系專業課程', '專業課程'])].index[0]
        row_end = self.pdf_df.shape[0]
        col_start = self.pdf_df.loc[:, self.pdf_df.iloc[0, :].isin(['一年級'])].columns[0]
        col_end = self.pdf_df.shape[1] - 1

        course_info = []
        for row in range(row_start, row_end):
            for col in range(col_start, col_end, 3):
                buffer = []
                buffer.append(get_cls(self.pdf_df, row, col))  # 課程類別
                buffer.append(get_type(self.pdf_df, row, col))  # 必選修
                buffer.append(get_category(self.pdf_df, row, col))  # 領域類別
                buffer.append(get_grade(self.pdf_df, row, col))  # 年級
                buffer.append(get_term(self.pdf_df, row, col))  # 學期
                buffer.append(self.pdf_df.iloc[row, col])  # 課程
                buffer.append(self.pdf_df.iloc[row, col + 1])  # 學分
                if col + 3 >= col_end:
                    if self.pdf_df.iloc[row, col + 2] is None:
                        try:
                            self.pdf_df.iloc[row, col + 2] = self.pdf_df.iloc[row, col + 3]
                        except:
                            pass
                buffer.append(self.pdf_df.iloc[row, col + 2])  # 時數

                course_info.append(buffer)

        course_df = pd.DataFrame(course_info)
        course_df.columns = ['課程類別', '必選修', '領域類別', '年級', '學期', '課程', '學分', '時數']
        self.pdf_df = course_df

    def clean_data(self):
        finally_df = self.pdf_df.drop(self.pdf_df[self.pdf_df['課程'].isin(['', None])].index)
        finally_df = finally_df.reset_index(drop=True)
        finally_df = pd.DataFrame(finally_df)
        self.pdf_df = finally_df

    def save_csv(self, output_dir, filename: str):
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        output_filename = f'extract - {filename}.csv'
        output = os.path.join(output_dir, output_filename)
        self.pdf_df.to_csv(output, encoding='utf-8-sig', index=False)

    def run_program(self):
        self.pdf_clean()
        self.make_dataframe()
        self.concat_dataframe()
        self.extract_data()
        self.clean_data()

    def get_df(self):
        return self.pdf_df

    def get_list(self):
        return self.pdf_cleaned
