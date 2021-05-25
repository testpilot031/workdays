""" 翌日がその月の何営業日目かを算出するスクリプト
    
    土日と祝日はカウントしません。
    祝日は内閣府がインターネット公開しているCSVをもとにしています。
    CSVは都度取りに行ってファイルとしてLambda実行マシン内の/tmp/に保存しています。
    ファイルは読み込んだ後に削除します。
    祝日の取得の仕方は内部のシステムから取得するなど今後検討。

    翌日が土日と祝日になる日にこの関数を実行した場合、それまでの営業日数が返ります。
    6/1(金)、6/2(土)の場合、5/31に実行すると1、6/1に実行すると1が返ります。

    pandasとnumpyはLinux版を入れてLambdaにアップしています。
    Windows版をアップすると動きません。
    *前提条件 
        一通り動くものとして作成しています。設計書はありません。
    
    ToDo:
        進行状況のログ出力(未対応)
        テスト項目を作ってテストしたい(未対応)
"""
import workdays
import pandas
import urllib.request
import datetime
import os

def get_holidays_list(
        # 内閣府の祝日CSVファイルを取得する。お手本にした文字列と変わっている以前はhttp
        holidays_jpn_url="https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv",
        # お手本にしたcolumn_nameと変わっていた
        column_name="国民の祝日・休日月日",
        encoding="SHIFT-JIS",
        update_csv=True):
    file_name = '/tmp/' + holidays_jpn_url.split("/")[-1]
    # csv保存
    urllib.request.urlretrieve(holidays_jpn_url, file_name)
    holidays_df = pandas.read_table(file_name, delimiter=",", encoding=encoding)
    os.remove(file_name)
    return holidays_df[column_name].tolist()

def get_holidays_datetime(
        holidays_jpn_url="https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv",
        column_name="国民の祝日・休日月日",
        encoding="SHIFT-JIS",
        update_csv=False):
    holidays_list = get_holidays_list(holidays_jpn_url, column_name, encoding,
                                      update_csv)
    # お手本にした文字列と変わっていた以前"%Y-%m-%d" 現在"%Y/%m/%d"
    return [datetime.datetime.strptime(h, "%Y/%m/%d") for h in holidays_list]

def lambda_handler(event, context):
    # タイムゾーンを設定
    JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
    # 当日とって翌日にする
    now_date_aware = datetime.datetime.now(JST)
    tomorrow_date_aware = now_date_aware + datetime.timedelta(days=1)
    tomorrow_date_native = datetime.datetime(int(tomorrow_date_aware.strftime('%Y')),
                int(tomorrow_date_aware.strftime('%m')),int(tomorrow_date_aware.strftime('%d')))
    # 月初
    first_date_aware = tomorrow_date_aware.replace(day=1)
    first_date_native = datetime.datetime(int(first_date_aware.strftime('%Y')),
                int(first_date_aware.strftime('%m')),int(first_date_aware.strftime('%d')))

    # 祝日情報（datetime.datetime型のリスト）を取得
    holidays = get_holidays_datetime()
    # 本日が第何営業日か返す
    return workdays.networkdays(first_date_native, tomorrow_date_native, holidays=holidays)

