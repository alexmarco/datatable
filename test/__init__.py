# -*- coding: utf-8 -*-
import csv

_test_csv = """
id,first_name,last_name,email,gender,ip_address
1,Diane,Harvey,dharvey0@soundcloud.com,Female,222.104.189.193
2,Keith,Frazier,kfrazier1@yahoo.com,Male,10.39.14.150
3,Margaret,Gonzales,mgonzales2@wufoo.com,Female,38.118.7.94
4,Lisa,Welch,lwelch3@salon.com,Female,77.26.29.189
5,James,Jenkins,jjenkins4@indiatimes.com,Male,7.106.49.156
6,Catherine,West,cwest5@cbslocal.com,Female,37.232.30.117
7,Roy,Chavez,rchavez6@cmu.edu,Male,232.151.103.111
8,Carl,Bradley,cbradley7@ca.gov,Male,22.174.35.28
9,Joshua,Moreno,jmoreno8@qq.com,Male,0.108.56.18
10,Patrick,Brooks,pbrooks9@biglobe.ne.jp,Male,112.31.72.217
11,Pamela,Daniels,pdanielsa@free.fr,Female,213.68.228.190
12,Willie,Wagner,wwagnerb@pinterest.com,Male,167.146.167.207
13,Shawn,Greene,sgreenec@europa.eu,Male,
14,Peter,Young,pyoungd@nydailynews.com,Male,64.47.202.94
15,Judith,Wallace,jwallacee@kickstarter.com,Female,
16,Jimmy,Woods,jwoodsf@guardian.co.uk,Male,38.109.102.233
17,Ashley,Wells,awellsg@com.com,Female,23.99.237.11
18,Louise,Walker,lwalkerh@is.gd,Female,194.222.255.217
19,Anne,Freeman,afreemani@sfgate.com,Female,157.197.225.102
20,Jimmy,Hayes,jhayesj@creativecommons.org,Male,1.58.202.143
21,Antonio,Mills,amillsk@acquirethisname.com,Male,139.24.16.160
22,Jose,Henry,jhenryl@diigo.com,Male,32.73.250.156
23,Jacqueline,Garza,jgarzam@vkontakte.ru,Female,33.172.249.243
24,Jimmy,Walker,jwalkern@usa.gov,Male,222.143.71.78
25,Kathleen,Perez,kperezo@guardian.co.uk,Female,212.188.223.66
"""

test_csv = list(csv.reader(_test_csv.split()))
