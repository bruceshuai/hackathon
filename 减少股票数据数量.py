import pandas as pd
# ===导入数据
df = pd.read_pickle('供选股数据.pkl')  # 从pickle文件中读取整理好的所有股票数据
df = df[df['上市至今交易天数'] > 250]
df = df[df['交易日期'] > '2013/1/1']
df.to_pickle('samll.pkl');
