#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'gmfork'

import re,time,os
from Config import *


class FetchVulInSF:
    '''
    查询securityfocus漏洞列表，url:http://www.securityfocus.com/
    '''
    def __init__(self):
        self.apiurl="http://www.securityfocus.com/cgi-bin/index.cgi?" \
                    "o={start}&l={lines}&c=12&op=display_list&" \
                    "vendor={vendor}&version={version}&title={title}&CVE={CVE}"
        self.oldurl=[]
        self.flag=False

        with open(ROOT+"/url.db","r") as f:
            while 1:
                buf=f.readline().strip()
                # print buf
                if not buf:
                    break
                self.oldurl.append(buf)

    def query(self,start,lines=100,date="",vendor="",version="",title="",CVE="",proxy=False):
        '''
        Parameters
        ----------
        start   起始位置
        lines   共查询多少条漏洞 最多100条  默认 100
        date    查询开始时间  范例2016-10-26 默认当前时间
        vendor  厂商  默认为空
        version 版本  默认为空
        title   漏洞标题  默认为空
        CVE     CVE号  默认为空

        Returns 漏洞url列表[title,date,url]
        -------
        '''
        if date=="":
            date=time.strftime("%Y-%m-%d")
        elif date=="null":
            date=""
        url=self.apiurl.format(start=start,lines=lines,vendor=vendor,
                               version=version,title=title,CVE=CVE)
        vuls=[]

        try:
            r=HTTPCONTAINER.get(url,proxy)
            pattern = re.compile(
                r'<a href="/bid/[0-9]+"><span class="headline">([\s\S]+?)</span></a><br/>\s*<span class="date">([0-9]{4}-[0-9]{2}-[0-9]{2})</span><br/>\s*<a href="/bid/[0-9]+">([\s\S]+?)</a><br/><br/>')
            results = pattern.findall(r.content)
            for result in results:
                # print result
                if result[2] in self.oldurl:
                    continue
                if date!="":
                    if time.strptime(result[1],"%Y-%m-%d") >= time.strptime(date,"%Y-%m-%d"):
                        vuls.append(result[2])
                    else:
                        self.flag=True
                else:
                    vuls.append(result[2])

            return vuls
        except:
            print "获取securityfocus漏洞列表出错"
            print '=== STEP ERROR INFO START'
            import traceback
            traceback.print_exc()
            print '=== STEP ERROR INFO END'
            return []
    def fetch(self,date,proxy=False):
        '''
        Parameters
        ----------
        date  2016-10-29

        Returns vuls list
        -------
        '''
        res = []
        t = 0
        num=0
        while 1:
            temp = self.query(t,date=date,proxy=proxy)
            num+=len(temp)

            LOG.pprint("+","Total fecth "+str(num),GREEN)

            if self.flag:
                res.extend(temp)
                break
            res += temp
            t += 100
        return res

    def fetchLine(self,lines,proxy=False):
        start=0
        res=[]
        while 1:
            temp=self.query(start,lines=100,date="null",proxy=proxy)
            num=len(temp)
            if num > lines:
                res.extend(temp[:lines])
                LOG.pprint("+", "Total fecth " + str(lines), GREEN)
                return res
            elif num==lines:#获取了足够的url
                res.extend(temp)
                LOG.pprint("+", "Total fecth " + str(lines), GREEN)
                return res
            else:
                start+=100
                lines-=num
                res.extend(temp)