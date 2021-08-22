# 提取課程結構規劃表

![overview](Overview.png)

## Overview

提取高雄科技大學電機工程系的課程結構規劃表，從 PDF 轉換特定內容到 CSV 格式，方便其他系統利用。

## Usage

建立 python 虛擬環境，並安裝依賴套件。

```
pip install -r requirements.txt
```

執行 `main.py` 來輸出提取課程結構規劃表。

- main.py

    主要程式，修改 `FILE_NAME` 來指定要轉換的檔案。

- input(pdf)

    輸入檔案的資料夾，輸入檔案必須是 pdf。

- output(csv)

    輸出檔案的資料夾，將以副檔名 csv 格式輸出。

