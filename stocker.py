#!/usr/bin/env python
# -*- encoding: utf-8 -*-
__author__ = 'odroid'

from bs4 import BeautifulSoup
import requests
from tabulate import tabulate
import time
from datetime import datetime
from time import mktime
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from config import stocks

user_agent = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/36.0.1985.125 Safari/537.36'}
url_mapa = 'http://www.ravaonline.com/v2/empresas/mapa.php'
try:
    r_mapa = requests.get(url_mapa, headers=user_agent)
    html_mapa = BeautifulSoup(r_mapa.text)
except requests.ConnectionError, e:
    print 'No se pudo conectar con el servidor. Error: %s' % e
    exit(1)

url_lider = 'http://ravaonline.com/v2/precios/panel.php?m=LID'
try:
    r_lider = requests.get(url_lider, headers=user_agent)
    html_lider = BeautifulSoup(r_lider.text)
except requests.ConnectionError, e:
    print 'No se pudo conectar con el servidor. Error: %s' % e
    exit(1)

url_gral = 'http://ravaonline.com/v2/precios/panel.php?m=GEN'
try:
    r_gral = requests.get(url_gral, headers=user_agent)
    html_gral = BeautifulSoup(r_gral.text)
except requests.ConnectionError, e:
    print 'No se pudo conectar con el servidor. Error: %s' % e
    exit(1)

now = datetime.now()
sum_ten_actual = 0
sum_ten_orig = 0
sum_gan_neta = 0
sum_ten_ayer = 0

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

    #busco el valor de cierre
    if html_lider.find(attrs={'class': "tablapanel"}) and html_lider.find(attrs={'class': "tablapanel"}).find('a', text=val):
        stock_close = html_lider.find(attrs={'class': "tablapanel"}).find('a', text=val).parent.parent.contents[7].string
    elif html_gral.find(attrs={'class': "tablapanel"}) and  html_gral.find(attrs={'class': "tablapanel"}).find('a', text=val):
        stock_close = html_gral.find(attrs={'class': "tablapanel"}).find('a', text=val).parent.parent.contents[7].string
    else:
        stock_close = '--'

    #busco el porcentaje actual en el mapa, panel lider o gral, en ese orden
    if (html_mapa.find(attrs={'class': 'td'+val})):
        percent_str = html_mapa.find(attrs={'class': 'td'+val}).find('span').string[:-1]
    elif html_lider.find(attrs={'class': "tablapanel"}) and html_lider.find(attrs={'class': "tablapanel"}).find('a', text=val):
        percent_str = html_lider.find(attrs={'class': "tablapanel"}).find('a', text=val).parent.parent.contents[5].string
        val += ' (*)'
    elif html_gral.find(attrs={'class': "tablapanel"}) and html_gral.find(attrs={'class': "tablapanel"}).find('a', text=val):
        percent_str = html_gral.find(attrs={'class': "tablapanel"}).find('a', text=val).parent.parent.contents[5].string
        val += ' (*)'
    else:
        percent_str = '--'



    if (type(stock_close) is str and '--' in stock_close) or (type(percent_str) is str and '--' in percent_str) or percent_str == '-':
        actual = '--'
        perc_mensual = '--'
        perc_gan = '--'
        gan_neta = '--'
        ten_orig = '--'
        ten_actual = '--'
        table.append([val, actual, percent_str,  ten_orig, ten_actual, perc_gan, gan_neta, days, perc_mensual])
    else:
        if ',' in stock_close:
            stock_close = float(stock_close.replace(',', '.'))

        if ',' in percent_str:
            percent = float(percent_str.replace(',', '.'))
        else:
            percent = float(percent_str)

        actual = stock_close*(percent/100+1)

        if type(stock) is dict:
            ten_actual = actual*stock['cant']
            ten_ayer = stock_close*stock['cant']
            perc_gan = (actual/float(stock['precio'])-1)*100

            if perc_gan > 0:
                perc_gan = '+'+str(perc_gan)
        else:
            ten_actual = 0
            ten_ayer = 0
            perc_gan = 0

        gan_neta = float(ten_actual-ten_orig)

        sum_ten_ayer += ten_ayer
        sum_ten_actual += ten_actual
        sum_ten_orig += ten_orig
        sum_gan_neta += gan_neta
        if percent > 0 and percent_str[0] != '+':
            percent_str = '+'+percent_str

        if days > 0:
            perc_mensual = 30*float(perc_gan)/days
        else:
            perc_mensual = 0

        actual = round(actual, 2)
        perc_mensual = round(perc_mensual, 2)
        perc_gan = round(float(perc_gan), 2)
        gan_neta = int(round(gan_neta))
        ten_orig = int(round(ten_orig))
        ten_actual = int(round(ten_actual))
        table.append([val, '$'+str(actual), str(percent_str)+'%',  '$'+str(ten_orig), '$'+str(ten_actual), str(perc_gan)+'%', '$'+str(gan_neta), str(days), str(perc_mensual)+'%'])

headers = ["Valor", "Actual", u"Variación", 'Ten. Orig', 'Ten. Actual', 'Porc. Gan', 'Gan. Neta', 'Días de ten.', 'Porc. Mens.']

perc_gan_total = round((sum_ten_actual/sum_ten_orig-1)*100, 2)
perc_gan_total = '+'+str(perc_gan_total) if sum_ten_actual > sum_ten_orig else str(perc_gan_total)
perc_gan_diaria = round((float(sum_ten_actual)/float(sum_ten_ayer)-1)*100, 2)
perc_gan_diaria = '+'+str(perc_gan_diaria) if sum_ten_actual > sum_ten_ayer else str(perc_gan_diaria)
sum_ten_orig = int(round(sum_ten_orig))
sum_ten_actual = int(round(sum_ten_actual))
sum_ten_ayer = int(round(sum_ten_ayer))
sum_gan_neta = int(round(sum_gan_neta))
gan_diaria = sum_ten_actual-sum_ten_ayer

print '\nValores a: %s\n' % now.strftime("%Y-%m-%d %H:%M")
print(tabulate(table, headers, tablefmt="orgtbl"))
print('\nTotal inicial: $%s' % sum_ten_orig)
print('Total actual: $%s' % sum_ten_actual)
print('Gan. Total Neta: $%s' % sum_gan_neta)
print('Gan. Diaria: $%s' % gan_diaria)
print('Gan. prop diaria: %s%%' % perc_gan_diaria)
print('Gan. prop total: %s%% \n' % perc_gan_total)
