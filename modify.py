# -*- coding: utf-8 -*-
'''
Author: Jimmy Chen
PN: Billing Tracker, Created Dec. 2017
Link:
Todo: 
''' 
# --------------------------------------------------- libs
import re
import sqlite3
import time, datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
from income import *
from expense import *
from account import *
from delete import *
import snippets as sp
# --------------------------------------------------- init settings
# --------------------------------------------------- Functions
class Modify(object):
    """docstring for Mod"""
    def __init__(self, arg):
        super(Mod, self).__init__()
        self.arg = arg
    def main(conn, table):
        print("-------------------")
        print("  Change -> {} ".format(table.capitalize()))
        print("-------------------")
        print("1. Monthly")
        print("2. Specific month")
        print("0. End")
        print("-------------------")
        check = int(input("Choose function: "))
        if check == 1:
            cMonth, nMonth = Show.month_init()
            end = True
            while end == True:
                print("===== {1} list (Month: {0}) =====".format(str(cMonth)[0:7], table.capitalize()))
                Show.ch_monthly(conn, check, cMonth, nMonth, table)
                print("--------------------------------------------------------------------------------------")
                print("1. Prev")
                print("2. Back")
                print("3. Modify")
                print("4. Delete")
                print("5. Quit")
                choose = int(input("Choose function: "))
                if choose == 1:
                    nMonth = cMonth
                    cMonth -= relativedelta(months=1)
                elif choose == 2:
                    cMonth = nMonth
                    nMonth += relativedelta(months=1)
                elif choose == 3:
                    id_ = int(input("Modify item(id): "))
                    Modify.run(conn, id_, cMonth, nMonth, table)
                elif choose == 4:
                    id_ = int(input("Delete item(id): "))
                    Delete.run(conn, id_, cMonth, nMonth, table)
                elif choose == 5:
                    end = False
                else:
                    print("Input error")
        elif check == 2:
            cyear = int(input("Which year: "))
            cmonth = int(input("Which month: "))
            cMonth, nMonth = sp.Tools.gen_timestamp(cyear, cmonth)
            end = True
            while end == True:
                print("===== {1} list (Month: {0}) =====".format(str(cMonth)[0:7], table.capitalize()))
                Show.ch_monthly(conn, check, cMonth, nMonth, table)
                print("--------------------------------------------------------------------------------------")
                print("1. Prev")
                print("2. Back")
                print("3. Modify")
                print("4. Delete")
                print("5. Quit")
                choose = int(input("Choose function: "))
                if choose == 1:
                    cmonth -= 1
                    if cmonth == 0:
                        cmonth = 12
                        cyear -= 1
                    cMonth, nMonth = sp.Tools.gen_timestamp(cyear, cmonth)
                elif choose == 2:
                    cmonth += 1
                    if cmonth == 13:
                        cmonth = 1
                        cyear += 1
                    cMonth, nMonth = sp.Tools.gen_timestamp(cyear, cmonth)
                elif choose == 3:
                    id_ = int(input("Modify item(id): "))
                    Modify.run(conn, id_, cMonth, nMonth, table)
                elif choose == 4:
                    id_ = int(input("Delete item(id): "))
                    Delete.run(conn, id_, cMonth, nMonth, table)
                elif choose == 5:
                    end = False
                else:
                    print("Input error")
    def adjust(conn, var, table):
        end = True
        while end == True:
            print("--------------------------------------------------------------------------------------")
            print("ID | Date | Time | Amount | Account | Main Category | Sub Category | Details | Invoice")
            print("--------------------------------------------------------------------------------------")
            print(' | '.join(var))
            print("--------------------------------------------------------------------------------------")
            print("1. Date")
            print("2. Amount")
            print("3. Account")
            print("4. Category")
            print("5. Details")
            print("6. Invoice")
            print("0. Make the change!")
            choose = int(input("Modify which column: "))
            if choose == 1:
                date_, time_ = sp.Tools.get_time('N')
                var[1] = date_
                var[2] = time_
            elif choose == 2:
                amount = int(input("Amount: "))
                var[3] = str(amount)
            elif choose == 3:
                Show.account(conn)
                acc = input("To account (No.): ")
                while (Acc.account_check(int(acc), conn) == False):
                    print("Account not exist!")
                    acc = input("To account (No.): ")
                else:
                    account = Acc.account_check(int(acc), conn)
                    var[4] = account
            elif choose == 4:
                if table == 'income':
                    print("----------------------------------------")
                    main = sp.Category_inc.get_main()
                    sub = sp.Category_inc.get_sub(main)
                    var[5], var[6] = main, sub
                if table == 'expense':
                    print("----------------------------------------")
                    main = sp.Category_exp.get_main()
                    sub = sp.Category_exp.get_sub(main)
                    var[5], var[6] = main, sub
            elif choose == 5:
                details = str(input("Details: ") or "None")
                var[7] = details
            elif choose == 6:
                invoice = str(input("Invoice: ") or "None")
                var[8] = invoice
            elif choose == 0:
                var[0] = sp.Tools.get_id(var[4], table, conn)
                var[3] = int(var[3])
                deal = []
                deal.append((var))
                sqlstr_inc_ent = ("INSERT OR IGNORE INTO {} (id, date, time, amount, account, main, sub, details, invoice) VALUES (?,?,?,?,?,?,?,?,?)".format(table))
                conn.executemany(sqlstr_inc_ent, deal)
                conn.commit()

                cur = conn.cursor()
                sqlstr_acc = "SELECT id FROM account WHERE title = '{0}';".format(var[4])
                cur.execute(sqlstr_acc)
                acc_id = cur.fetchone()[0]
                Acc.adjust(acc_id, conn, table, var[3])
                print("Recorded!\n")
                end = False
            else:
                print("Input error")

    def run(conn, id, curMonth, nextMonth, table):
        cur = conn.cursor()
        sqlstr = "SELECT * FROM {1} WHERE id == {0}".format(id, table)
        cur.execute(sqlstr)
        var = cur.fetchall()
        item = [str(_) for _ in list(var[0])]
        Modify.adjust(conn, item, table)
        title_, amount_ = var[0][4], var[0][3]
        Delete.reverse(conn, table, title_, amount_)
        if len(var) == 0:
            print("No item {}!".format(id))
        else:
            sqlstr = "DELETE FROM {1} WHERE id = {0}".format(id, table)
            cur.execute(sqlstr)
            print("Item {} is delete!".format(id))
        conn.commit()