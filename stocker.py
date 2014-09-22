#!/usr/bin/env python
# -*- encoding: utf-8 -*-
__author__ = 'odroid'

from bs4 import BeautifulSoup
import requests
from tabulate import tabulate
import time
import time
from datetime import datetime
from time import mktime
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

stocks = [{'val': 'ERAR',
           'cant': 1,
           'precio': 5,
           'fecha': '16-09-2010'},
          {'val': 'BMA',
           'cant': 1,
           'precio': 5,
           'fecha': '16-09-2010'},
          {'val': 'TS',
           'cant': 1,
           'precio': 32,
           'fecha': '22-09-2010'},
           'EDN', 'BRIO', 'APBR', 'YPFD', 'PAMP', 'COME', 'TECO2', 'GGAL', 'PATA']

url_mapa = 'http://www.ravaonline.com/v2/empresas/mapa.php'
user_agent = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'}
r_mapa = requests.get(url_mapa, headers=user_agent)
html_mapa = BeautifulSoup(r_mapa.text)

url_lider = 'http://ravaonline.com/v2/precios/panel.php?m=LID'
r_lider = requests.get(url_lider, headers=user_agent)
html_lider = BeautifulSoup(r_lider.text)

url_gral = 'http://ravaonline.com/v2/precios/panel.php?m=GEN'
r_gral = requests.get(url_gral, headers=user_agent)
html_gral = BeautifulSoup(r_gral.text)


sum_ten_actual = 0
sum_ten_orig = 0
sum_gan_neta = 0

table = []

for stock in stocks:
    if type(stock) is dict:
        val = str(stock['val'])
        ten_orig = stock['cant']*stock['precio']
        date_from = time.strptime(stock['fecha'], "%d-%m-%Y")
        date_from = datetime.fromtimestamp(mktime(date_from))
        date_today = datetime.fromtimestamp(mktime(time.localtime()))
        date_diff = date_today - date_from
        days = date_diff.days
    else:
        val = stock
        ten_orig = 0
        days = 0
    try:
        stock_close = html_lider.find(attrs={'class': "tablapanel"}).find('a', text=val).parent.parent.contents[7].string
    except:
        stock_close = html_gral.find(attrs={'class': "tablapanel"}).find('a', text=val).parent.parent.contents[7].string

    delayed = False

    if (html_mapa.find(attrs={'class': 'td'+val})):
        percent_str = html_mapa.find(attrs={'class': 'td'+val}).find('span').string
    elif (html_lider.find(attrs={'class': "tablapanel"}).find('a', text=val)):
        percent_str = html_lider.find(attrs={'class': "tablapanel"}).find('a', text=val).parent.parent.contents[5].string
        delayed = True
    else:
        percent_str = html_gral.find(attrs={'class': "tablapanel"}).find('a', text=val).parent.parent.contents[5].string
        delayed = True

    if delayed:
        val = val+' (*)'
    stock_close = float(stock_close.replace(',', '.'))
    percent_str = percent_str[:-1]
    percent = float(percent_str.replace(',', '.'))
    actual = round(stock_close*(percent/100+1), 2)

    if type(stock) is dict:
        ten_actual = actual*stock['cant']
        perc_gan = round((actual/float(stock['precio'])-1)*100, 2)
        if perc_gan > 0:
            perc_gan = '+'+str(perc_gan)
    else:
        ten_actual = 0
        perc_gan = 0

    gan_neta = int(round(ten_actual-ten_orig))

    sum_ten_actual += ten_actual
    sum_ten_orig += ten_orig
    sum_gan_neta += gan_neta
    if percent > 0 and percent_str[0] != '+':
        percent_str = '+'+percent_str

    if days > 0:
        perc_mensual = round(30*float(perc_gan)/days, 2)
    else:
        perc_mensual = 0

    table.append([val, '$'+str(actual), str(percent_str)+'%',  '$'+str(ten_orig), '$'+str(ten_actual), str(perc_gan)+'%', '$'+str(gan_neta), str(days), str(perc_mensual)+'%'])

headers = ["Valor", "Actual", u"Variación", 'Ten. Orig', 'Ten. Actual', 'Porc. Gan', 'Gan. Neta', 'Días de ten.', 'Porc. Mens.']
print tabulate(table, headers, tablefmt="orgtbl")
print '\n'
print 'Total inicial: %s' % int(round(sum_ten_orig))
print 'Total actual: %s' % int(round(sum_ten_actual))
print 'Gan. Total Neta: %s \n' % int(round(sum_gan_neta))
