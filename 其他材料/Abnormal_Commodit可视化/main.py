from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)
# init
df06p = pd.read_excel('./database/df06p.xlsx')
df07p = pd.read_excel('./database/df07p.xlsx')
df08p = pd.read_excel('./database/df08p.xlsx')
df09p = pd.read_excel('./database/df09p.xlsx')
df06s = pd.read_excel('./database/df06s.xlsx')
df07s = pd.read_excel('./database/df07s.xlsx')
df08s = pd.read_excel('./database/df08s.xlsx')
df09s = pd.read_excel('./database/df09s.xlsx')


@app.route('/map', methods=['GET'])
def map_of_china():
    dfp = df06p.append(df07p).append(df08p).append(df09p)
    dfs = df06s.append(df07s).append(df08s).append(df09s)
    provinces = ['上海', '青海', '云南', '其他', '内蒙古', '北京', '台湾', '吉林', '四川', '天津', '宁夏', '安徽', '山东', '山西', '广东', '广西', '新疆',
                 '江苏',
                 '江西', '河北', '河南', '浙江', '海南', '湖北', '湖南', '澳门', '甘肃', '福建', '西藏', '贵州', '辽宁', '重庆', '陕西', '香港', '黑龙江']
    df = dfp.append(dfs)
    ls = set(dfp['SHOP_DELIVERY_PROVINCE'].to_list())
    ans1 = list()
    ans2 = list()
    cou = 0
    for i in ls:
        for j in provinces:
            if j in i:
                if j != '其他':
                    ans1.append(
                        {'id': cou, 'name': j, 'value': str(df[df.SHOP_DELIVERY_PROVINCE == i]['ITEM_ID'].count())})
                else:
                    ans2.append(
                        {'id': cou, 'name': j, 'value': str(df[df.SHOP_DELIVERY_PROVINCE == i]['ITEM_ID'].count())})
                cou += 1
                break
    return jsonify({'provinces': ans1, 'other': ans2})


@app.route('/polyline', methods=['GET'])
def abnormal_items_per_month():
    dfp = df06p.append(df07p).append(df08p).append(df09p)
    dfs = df06s.append(df07s).append(df08s).append(df09s)
    result = list()
    data = []
    ls = set(dfp.DATA_MONTH)
    for i in ls:
        data.append(int(dfp[dfp.DATA_MONTH == i]['ITEM_ID'].count()))
    result.append({'name': "价格异常", 'data': data.copy()})
    data = []
    for i in ls:
        data.append(int(dfs[dfs.DATA_MONTH == i]['ITEM_ID'].count()))
    result.append({'name': "销量异常", 'data': data.copy()})
    return jsonify({'countdata': result})


@app.route('/total', methods=['GET'])
def abnormal_total():
    referdata = []
    ms = {202106: '4503234', 202107: '4133200', 202108: '4286325', 202109: '4412327', }
    dfp = df06p.append(df07p).append(df08p).append(df09p)
    dfs = df06s.append(df07s).append(df08s).append(df09s)
    df = dfp.append(dfs)
    data = []
    ls = set(df.DATA_MONTH)
    for i in ls:
        data.append({'month': str(i), 'total': ms.get(i), 'abnormalTotal': str(df[df.DATA_MONTH == i]['ITEM_ID'].count())})
    referdata.append({'name': "商品库", 'data': data.copy()})
    data = []
    for i in ls:
        data.append({'month': str(i), 'total': ms[i], 'abnormalTotal': str(dfp[dfp.DATA_MONTH == i]['ITEM_ID'].count())})
    referdata.append({'name': "价格库", 'data': data.copy()})
    data = []
    for i in ls:
        data.append({'month': str(i), 'total': ms[i], 'abnormalTotal': str(dfs[dfs.DATA_MONTH == i]['ITEM_ID'].count())})
    referdata.append({'name': "商品库", 'data': data.copy()})
    return jsonify({"referdata": referdata})


@app.route('/detail', methods=['GET'])
def abnormal_detail_info():
    dfp = df06p.append(df07p).append(df08p).append(df09p)
    dfs = df06s.append(df07s).append(df08s).append(df09s)
    df = dfp.append(dfs)
    ls = set(df['SHOP_DELIVERY_PROVINCE'].to_list())
    province = request.args.get('province')
    print(province)
    data = []
    for k in ls:
        if province in k:
            dt = dfp[dfp.SHOP_DELIVERY_PROVINCE == k].loc[:,
                 ['DATA_MONTH', 'ITEM_ID', 'ITEM_NAME', 'BRAND_NAME', 'CATE_NAME_LV1', 'SHOP_NAME']]
            dt = dt.reset_index(drop=True)
            for i in dt.index:
                data.append(
                    {"id": str(dt.loc[i, 'ITEM_ID']), 'month': str(dt.loc[i, 'DATA_MONTH']), 'name': dt.loc[i, 'ITEM_NAME'],
                     'brand': dt.loc[i, 'BRAND_NAME'], 'category': dt.loc[i, 'CATE_NAME_LV1'],
                     'shop': dt.loc[i, 'SHOP_NAME'], 'type': '价格异常'})
            dt = dfs[dfs.SHOP_DELIVERY_PROVINCE == k].loc[:,
                 ['DATA_MONTH', 'ITEM_ID', 'ITEM_NAME', 'BRAND_NAME', 'CATE_NAME_LV1', 'SHOP_NAME']]
            dt = dt.reset_index(drop=True)
            for i in dt.index:
                data.append(
                    {"id": str(dt.loc[i, 'ITEM_ID']), 'month': str(dt.loc[i, 'DATA_MONTH']), 'name': dt.loc[i, 'ITEM_NAME'],
                     'brand': dt.loc[i, 'BRAND_NAME'], 'category': dt.loc[i, 'CATE_NAME_LV1'],
                     'shop': dt.loc[i, 'SHOP_NAME'], 'type': '销量异常'})
            data.sort(key=lambda x: x.get('id'))
            break
    return jsonify({'listData': data})


@app.route('/salerate', methods=['GET'])
def abnormal_sale_info():
    c1 = []
    dfs = df06s.append(df07s).append(df08s).append(df09s)
    Lv1 = set(dfs.CATE_NAME_LV1)
    for i in Lv1:
        Lv2 = set(dfs[dfs.CATE_NAME_LV1 == i].CATE_NAME_LV2)
        dfslv2 = dfs[dfs.CATE_NAME_LV1 == i]
        c2 = []
        for j in Lv2:
            Lv3 = set(dfslv2[dfslv2.CATE_NAME_LV2 == j].CATE_NAME_LV3)
            dfslv3 = dfslv2[dfslv2.CATE_NAME_LV2 == j]
            c3 = []
            for k in Lv3:
                Lv4 = set(dfslv3[dfslv3.CATE_NAME_LV3 == k].CATE_NAME_LV4)
                dfslv4 = dfslv3[dfslv3.CATE_NAME_LV3 == k]
                c4 = []
                for m in Lv4:
                    Lv5 = set(dfslv4[dfslv4.CATE_NAME_LV4 == m].CATE_NAME_LV5)
                    dfslv5 = dfslv4[dfslv4.CATE_NAME_LV4 == m]
                    c5 = []
                    for q in Lv5:
                        dflv = dfslv5[dfslv5.CATE_NAME_LV5 == q]
                        c5.append({"value": int(dflv['ITEM_ID'].count()), "name": q})
                    c4.append({"value": int(dfslv5['ITEM_ID'].count()), "name": m, "children": c5.copy()})
                c3.append({"value": int(dfslv4['ITEM_ID'].count()), "name": k, "children": c4.copy()})
            c2.append({"value": int(dfslv3['ITEM_ID'].count()), "name": j, "children": c3.copy()})
        c1.append({"value": int(dfslv2['ITEM_ID'].count()), "name": i, "children": c2.copy()})
    return jsonify({"salerateData": c1})


def get_stats(group):
    return {'count': group.count()}

@app.route('/heatmap', methods=['GET'])
def abnormal_price_heatmap():
    dfp = df06p.append(df07p).append(df08p).append(df09p)
    dfp['lv'] = dfp['CATE_NAME_LV1'] + dfp['CATE_NAME_LV2'] + dfp['CATE_NAME_LV3'] + dfp['CATE_NAME_LV4'] + dfp[
        'CATE_NAME_LV5']
    dflv = dfp.groupby('lv')['ITEM_ID'].count().sort_values(ascending=False)
    category = dflv.index[:12].tolist()
    price = [0, 10, 100, 500, 1000, 5000, 10000, max(dfp.ITEM_PRICE)]
    data = []
    for i in range(len(category)):
        df = dfp[dfp.lv == category[i]]
        quartiles_price = pd.cut(df.ITEM_PRICE, bins=price, duplicates="drop")
        grouped = df['ITEM_PRICE'].groupby([quartiles_price])
        grouped.apply(get_stats).unstack()
        gd = grouped.apply(get_stats).unstack()
        ls = gd['count'].tolist()
        for j in range(len(ls)):
            data.append([i, j, ls[j]])
    price = list(map(str, price[:-1]))
    return jsonify({"category": category, "price": price, "data": data})


if __name__ == '__main__':
    app.run(port=5000, debug=True)
