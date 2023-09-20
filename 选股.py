import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ===选股参数设定
select_stock_num = 3  # 第一轮选股数量
select_stock_num2 = 3
c_rate = 1.2 / 10000  # 手续费，手续费>万1.2
t_rate = 1 / 1000  # 印花税


# ===导入数据
df = pd.read_pickle('选股数据.pkl')  # 从pickle文件中读取整理好的所有股票数据
print(df)


# ===构建选股因子
df['因子'] = df['总市值'] * df['成交额std_10']

# ===对股票数据进行筛选
df = df[df['上市至今交易天数'] > 250]  # 删除上市不满一年的股票

#df = df[df['申万一级行业名称'].isin(['通信'])]  # 对所在行业进行筛选
# # '钢铁', '交通运输', '房地产', '公用事业', '化工', '休闲服务', '医药生物', '商业贸易', '食品饮料', '家用电器', '轻工制造', '纺织服装', '综合', '农林牧渔', '有色金属', '采掘', '电子', '银行', '汽车', '非银金融', '机械设备', '传媒', '国防军工', '建筑装饰', '通信', '电气设备', '计算机', '建筑材料'

df = df[df['现金流量净额(经营活动)']> 0] #对财务数据进行筛选
#df = df[df['振幅_10'] >0.1] #对财务数据进行筛选 > 1000
df = df[df['振幅_5'] >0.05] #对财务数据进行筛选

#df = df[df['归母净利润'] >0 ] #对财务数据进行筛选


# ===选股
df['排名'] = df.groupby('交易日期')['因子'].rank()  # 根据选股因子对股票进行排名
df = df[df['排名'] <= select_stock_num]  # 选取排名靠前的股票

# df['因子'] = df['总市值'] * df['成交额std_10']
# df['排名'] = df.groupby('交易日期')['因子'].rank()  # 根据选股因子对股票进行排名
# df = df[df['排名'] <= select_stock_num2]  # 选取排名靠前的股票

# ===整理选中股票数据，计算涨跌幅
# 挑选出选中股票
df['股票代码'] += ' '
df['股票名称'] += ' '
group = df.groupby('交易日期')

#df.to_csv('stock_data.csv', index=False)

select_stock = pd.DataFrame()
select_stock['买入股票代码'] = group['股票代码'].sum()
select_stock['买入股票名称'] = group['股票名称'].sum()

# 计算下周期每天的资金曲线
select_stock['选股下周期每天资金曲线'] = group['下周期每天涨跌幅'].apply(lambda x: np.cumprod(np.array(list(x))+1, axis=1).mean(axis=0))
# 扣除买入手续费
select_stock['选股下周期每天资金曲线'] = select_stock['选股下周期每天资金曲线'] * (1 - c_rate)  # 计算有不精准的地方
# 扣除卖出手续费、印花税。最后一天的资金曲线值，扣除印花税、手续费
select_stock['选股下周期每天资金曲线'] = select_stock['选股下周期每天资金曲线'].apply(lambda x: list(x[:-1]) + [x[-1] * (1 - c_rate - t_rate)])
# 计算下周期整体涨跌幅
select_stock['选股下周期涨跌幅'] = select_stock['选股下周期每天资金曲线'].apply(lambda x: x[-1] - 1)
del select_stock['选股下周期每天资金曲线']
# 计算整体资金曲线
select_stock.reset_index(inplace=True)
select_stock['资金曲线'] = (select_stock['选股下周期涨跌幅'] + 1).cumprod()
print(select_stock)


# ===画图
select_stock.set_index('交易日期', inplace=True)
plt.plot(select_stock['资金曲线'])
plt.show()
