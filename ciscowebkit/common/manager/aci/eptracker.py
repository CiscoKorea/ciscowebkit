#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#        _____ _                  _____           _                            #
#       / ____(_)                / ____|         | |                           #
#      | |     _ ___  ___ ___   | (___  _   _ ___| |_ ___ _ __ ___  ___        #
#      | |    | / __|/ __/ _ \   \___ \| | | / __| __/ _ \ '_ ` _ \/ __|       #
#      | |____| \__ \ (_| (_) |  ____) | |_| \__ \ ||  __/ | | | | \__ \       #
#       \_____|_|___/\___\___/  |_____/ \__, |___/\__\___|_| |_| |_|___/       #
#                                        __/ |                                 #
#                                       |___/                                  #
#           _  __                       _____       _  _____ ______            #
#          | |/ /                      / ____|     | |/ ____|  ____|           #
#          | ' / ___  _ __ ___  __ _  | (___   ___ | | (___ | |__              #
#          |  < / _ \| '__/ _ \/ _` |  \___ \ / _ \| |\___ \|  __|             #
#          | . \ (_) | | |  __/ (_| |  ____) | (_) | |____) | |____            #
#          |_|\_\___/|_|  \___|\__,_| |_____/ \___/|_|_____/|______|           #
#                                                                              #
################################################################################
#                                                                              #
# Copyright (c) 2016 Cisco Systems                                             #
# All Rights Reserved.                                                         #
#                                                                              #
# Licensed under the Apache License, Version 2.0 (the "License"); you may      #
# not use this file except in compliance with the License. You may obtain      #
# a copy of the License at                                                     #
#                                                                              #
# http://www.apache.org/licenses/LICENSE-2.0                                   #
#                                                                              #
# Unless required by applicable law or agreed to in writing, software          #
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the  #
#    License for the specific language governing permissions and limitations   #
#    under the License.                                                        #
#                                                                              #
################################################################################

'''
Created on 2016. 8. 17.

@author: "comfact"
'''

import re
import pymysql
import warnings

from ciscowebkit.common.pygics import *
from ciscowebkit.common.manager.aci import acitoolkit as acitool


class EPTracker(Task):
    
    class APIC_CONNECTION_FAILED(E):
        def __init__(self, apic): E.__init__(self, 'Connection Failed %s@%s:%s' % (apic.user, str(apic.ips), apic.pwd))
         
    class DB_CONNECTION_FAILED(E):
        def __init__(self): E.__init__(self, 'Access Denied Persistent Data')
        
    def __init__(self, apic):
        Task.__init__(self, 2, 2)
        self._apic = apic
        self._session = acitool.Session('https://%s' % apic.connected, apic.user, apic.pwd)
        resp = self._session.login()
        if not resp.ok:
            self._session.close()
            raise EPTracker.APIC.APIC_CONNECTION_FAILED(apic)
        self._table_name = 'aci_%s_eptracker' % apic.domain
        try:
            self._db = pymysql.connect(user='cisco', password='cisco123', host='localhost')
        except:
            self._db.close()
            self._session.close()
            raise EPTracker.DB_CONNECTION_FAILED()
        
        cursor = self._db.cursor()
        cursor.execute('USE ciscowebkit;')
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            cursor.execute('''CREATE TABLE IF NOT EXISTS %s (
                                    mac       CHAR(18) NOT NULL,
                                    ip        CHAR(16),
                                    tenant    CHAR(100) NOT NULL,
                                    app       CHAR(100) NOT NULL,
                                    epg       CHAR(100) NOT NULL,
                                    interface CHAR(100) NOT NULL,
                                    timestart TIMESTAMP NOT NULL,
                                    timestop  TIMESTAMP);''' % self._table_name)
            self._db.commit()
        endpoints = acitool.Endpoint.get(self._session)
        for ep in endpoints:
            try: epg = ep.get_parent()
            except AttributeError: continue
            app_profile = epg.get_parent()
            tenant = app_profile.get_parent()
            if ep.if_dn:
                for dn in ep.if_dn:
                    match = re.match('protpaths-(\d+)-(\d+)', dn.split('/')[2])
                    if match:
                        if match.group(1) and match.group(2):
                            int_name = "Nodes: " + match.group(1) + "-" + match.group(2) + " " + ep.if_name
                            pass
            else: int_name = ep.if_name
            try: data = (self._table_name, ep.mac, ep.ip, tenant.name, app_profile.name, epg.name, int_name, self.convert_timestamp_to_mysql(ep.timestamp))
            except ValueError, e: print str(e); continue
            ep_exists = cursor.execute('''SELECT * FROM %s WHERE mac="%s" AND timestop="0000-00-00 00:00:00";''' % (self._table_name, ep.mac))
            cursor.fetchall()
            if not ep_exists:
                cursor.execute('''INSERT INTO %s (mac, ip, tenant, app, epg, interface, timestart) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s");''' % data)
                self._db.commit()
        cursor.close()
        acitool.Endpoint.subscribe(self._session)
        self.start()
    
    def __del__(self):
        self.stop()
        self._db.close()
        self._session.close()
        
    def __call__(self):
        ret = L()
        cursor = self._db.cursor()
        try:
            cursor.execute('USE ciscowebkit;')
            cursor.execute('SELECT * FROM %s;' % self._table_name)
        except:
            self._db.close()
            self._db = pymysql.connect(user='cisco', password='cisco123', host='localhost')
            cursor = self._db.cursor()
            cursor.execute('USE ciscowebkit;')
            cursor.execute('SELECT * FROM %s;' % self._table_name)
        for row in cursor: ret << M(mac=row[0], epg=row[2] + '/' + row[3] + '/' + row[4], ip=row[1], interface=row[5], timestart=str(row[6]), timestop=str(row[7]))
        cursor.close()
        return ret
        
    def task(self):
        while True:
            try:
                if acitool.Endpoint.has_events(self._session):
                    ep = acitool.Endpoint.get_event(self._session)
                    try: epg = ep.get_parent()
                    except AttributeError: continue
                    app_profile = epg.get_parent()
                    tenant = app_profile.get_parent()
                    cursor = self._db.cursor()
                    if ep.is_deleted():
                        ep.if_name = None
                        data = (self._table_name, self.convert_timestamp_to_mysql(ep.timestamp), ep.mac, tenant.name)
                        try: cursor.execute('''UPDATE %s SET timestop="%s", timestart=timestart WHERE mac="%s" AND tenant="%s" AND timestop="0000-00-00 00:00:00";''' % data)
                        except:
                            self._db.close()
                            self._db = pymysql.connect(user='cisco', password='cisco123', host='localhost')
                            cursor = self._db.cursor()
                            cursor.execute('''UPDATE %s SET timestop="%s", timestart=timestart WHERE mac="%s" AND tenant="%s" AND timestop="0000-00-00 00:00:00";''' % data)
                    else:
                        if ep.if_dn:
                            for dn in ep.if_dn:
                                match = re.match('protpaths-(\d+)-(\d+)', dn.split('/')[2])
                                if match:
                                    if match.group(1) and match.group(2):
                                        int_name = "Nodes: " + match.group(1) + "-" + match.group(2) + " " + ep.if_name
                                        pass
                        else: int_name = ep.if_name
                        data = (self._table_name, ep.mac, ep.ip, tenant.name, app_profile.name, epg.name, int_name, self.convert_timestamp_to_mysql(ep.timestamp))
                        
                        try: cursor.execute('''SELECT COUNT(*) FROM %s WHERE mac="%s" AND ip="%s" AND tenant="%s" AND app="%s" AND epg="%s" AND interface="%s" AND timestart="%s";''' % data)
                        except:
                            self._db.close()
                            self._db = pymysql.connect(user='cisco', password='cisco123', host='localhost')
                            cursor = self._db.cursor()
                            cursor.execute('''SELECT COUNT(*) FROM %s WHERE mac="%s" AND ip="%s" AND tenant="%s" AND app="%s" AND epg="%s" AND interface="%s" AND timestart="%s";''' % data)
                        for count in self._cursor:
                            if not count[0]:
                                cursor.execute('''INSERT INTO %s (mac, ip, tenant, app, epg, interface, timestart) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s");''' % data)
                    self._db.commit()
                    cursor.close()
                else: break
            except: break
    
    def convert_timestamp_to_mysql(self, timestamp):
        (resp_ts, remaining) = timestamp.split('T')
        resp_ts += ' '
        resp_ts = resp_ts + remaining.split('+')[0].split('.')[0]
        return resp_ts