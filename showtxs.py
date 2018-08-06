#!/usr/bin/python


from dboperations import *
import datetime
from Tkinter import *
from ttk import *

class App(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.ShowTransactions()
        self.grid(sticky = (N,S,W,E))
        parent.grid_rowconfigure(0, weight = 1)
        parent.grid_columnconfigure(0, weight = 1)

    def ShowTransactions(self):
        tv = Treeview(self)
        tv['columns'] = ('type', 'action', 'time', 'value')
        tv.heading("#0", text='Hash', anchor='w')
        tv.column("#0", anchor="w")
        tv.heading('type', text='Type')
        tv.column('type', anchor='center', width=100)
        tv.heading('action', text='Action')
        tv.column('action', anchor='center', width=100)
        tv.heading('time', text='Time')
        tv.column('time', anchor='center', width=100)
        tv.heading('value', text='Value')
        tv.column('value', anchor='center', width=100)
        tv.grid(sticky = (N,S,W,E))
        self.treeview = tv
        self.grid_rowconfigure(0, weight = 2)
        self.grid_columnconfigure(0, weight = 2)

        self.LoadTransactions()

    def LoadTransactions(self):

        txs = CWalletDB().GetTxs()

        for tx in txs:
            txhash = tx[0]
            
            self.treeview.insert('', 'end', text=txhash, values=(CTx(txhash).GetType(),
                                                                 CWalletDB().SpendOrReceive(txhash),
                                                                 datetime.datetime.fromtimestamp(int(CTx(txhash).Time())).strftime('%Y-%m-%d %H:%M:%S'), 
                                                                 CTx(txhash).Value() / COIN, ))

def main():
    root = Tk()
    App(root)
    root.title("Transactions")
    root.mainloop()

if __name__ == '__main__':
    main()
