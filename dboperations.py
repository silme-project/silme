#!/usr/bin/python
# Copyright (c) 2018 CVSC
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import sqlite3 
from sqlitetemplates import *
from utils import *
from consensus import *




class CDB(object):
    def __init__(self, database):
        self.conn = sqlite3.connect(GetAppDir() + "/" + database)
        self.conn.text_factory = str
        self.cur = self.conn.cursor()
        self.templates = Templates()
    # CDB basic operations
    def Exec(self, statment, values=None):
        if not values:
            try:
                self.cur.execute(statment)
            except Exception as e:
                logg(e)
                return False
            else:
                self.conn.commit()
                return True
        else:
            try:
                self.cur.execute(statment, (values))
            except Exception as e:
                logg(e)
                return False 
            else:
                self.conn.commit()
                return True

    def Read(self, statment, values=False):
        if values:
            return self.cur.execute(statment, (values))
        else:
            return self.cur.execute(statment)


class CBlockchain(CDB):
    def __init__(self, Genesis = None, db = "blockchain.db"):
        self.self = CDB.__init__(self, db)
        self.Exec(self.templates.blockchain["blocks"])
        self.Exec(self.templates.blockchain["transactions"])

        if Genesis:
            # init genesis block 
            if not self.Exec(self.templates.blockchain["writeblock"], (1, "000009cb25c348b85b01819c52402adea224580263fbe9b915be8502c5220f82", "0100000000000000000000000000000000000000000000000000000000000000000000007a98ffba469fe652771c5bb7b236248b4d78e4127ef369f1b07e1071da069e2fba756b5affff0f1ef7830e00", 0)):
                sys.exit(logg("Unable to initialize genesis block"))
    

    def WriteTxs(self, pblock):
        ntx = len(pblock.vtx)
        height = self.getBestHeight()
        for x in xrange(0,ntx):
            txhash = hashlib.sha256(hashlib.sha256(str(pblock.vtx[x])).hexdigest()).hexdigest()
            try:
               self.Exec(self.templates.blockchain["inserttx"], (height, pblock.vtx[x]["version"],pblock.vtx[x]["prev_out"],pblock.vtx[x]["time"], pblock.vtx[x]["value"], txhash, pblock.vtx[x]["input_script"], pblock.vtx[x]["output_script"], pblock.vtx[x]["signature"])) # Insert a row of data
               # check if we receive or if we spend coins at this tx and add tx hash to wallet db 
               if CWalletDB().isMineTx(txhash):
                  CWalletDB().AddTx(txhash)
            except Exception as e:
                logg(e)
                return False
            else:
                pass
        return True
            

        


    def WriteBlock(self, pblock, raw, nonce):
        thisHeight = self.getBestHeight() + 1
        thishash = hashlib.sha256(hashlib.sha256(raw).digest()).digest()[::-1].encode('hex_codec')
        blk = self.Exec(self.templates.blockchain["writeblock"], (thisHeight, thishash, raw, nonce))
        txs = self.WriteTxs(pblock)
        if blk == True and txs == True:
            return True
        logg("Failed to write block or txs")
        return False 


    def isVaildTx(self, tx):

        # transaction value 
        amount = tx["value"]
        # transaction time
        itime = tx["time"]
        # store signature in memory
        signature = tx["signature"]
        # remove signature from tx 
        del tx['signature']

        
        # transaction input hash value
        res = CTx(tx["prev_out"]).Value()
        # transaction input hash pubkey
        pub = CTx(tx["prev_out"]).GetRecipten()


        # if the input hash value < transaction value or transaction time < the current time transaction return is not vaild
        if not res or res < amount or itime > int(time.time()):
            return False

        # transaction verification, True if verify False if not
        if ecdsa_verify(str(tx),signature,pub):
           # add signature to tx 
           tx['signature'] = signature
           return True
        return False



    def getBestHeight(self):
        return len(self.Read(self.templates.blockchain["bestheight"]).fetchall())


    def GetBestHash(self):
        return self.Read(self.templates.blockchain["besthash"]).fetchall()[len(self.Read(self.templates.blockchain["besthash"]).fetchall()) -1][0]


    def haveHash(self, hash):
        return hash in str(self.Read(self.templates.blockchain["havehash"]).fetchall())


    def GetBlock(self, height):
        return self.Read(self.templates.blockchain["getblock"],[height]).fetchone()


    def GetTxsByKey(self, key):
        transactions = []
        for x in xrange(2, self.getBestHeight() +1):
            txs = CBlockIndex(x).Txs()
            for tx in txs:
                if key in CTx(tx[5]).GetRecipten():
                    if CTx(tx[5]).isCoinbase():
                        sender = "Coinbsase"
                    else: 
                        sender = CTx(tx[5]).GetSender()
                        
                    transactions.append({"hash": tx[5], 
                                         "type": "receive", 
                                         "value": CTx(tx[5]).Value(),
                                         "sender": sender,
                                         "time": CTx(tx[5]).Time(),
                                         "block height": CTx(tx[5]).Height()
                                         })
        return transactions


    def GetBalance(self, key):
        txss = {}
        balance = 0
        for x in xrange(2, self.getBestHeight() +1):
            txs = CBlockIndex(x).Txs()
            for tx in txs:
                if key in CTx(tx[5]).GetRecipten():
                    txss[tx[5]] = CTx(tx[5]).Value()
                    
        for x in xrange(2, self.getBestHeight() +1):
            txs = CBlockIndex(x).Txs()
            for tx in txs:
                if not CTx(tx[5]).isCoinbase():
                    if CTx(tx[5]).GetSender() == key:
                        txss[CTx(tx[5]).Prev()] -= CTx(tx[5]).Value() * COIN

        return float(sum(txss.values()) / COIN) 
















class CWalletDB(CDB):
    def __init__(self, db = "wallet.db"):
        self.self = CDB.__init__(self, db)
        self.Exec(self.templates.wallet["keys"])
        self.Exec(self.templates.wallet["txs"]) 
    # CDB basic operations    

    
    def WriteKey(self, key, pubkey):
        # Write a specifiec pubkey and its privkey to database  
        return self.Exec(self.templates.wallet["addkeys"], (key, pubkey))
    
    def IsMineKey(self, pubkey):
        # Return True if the given public key is our 
        return pubkey in str(self.Read(self.templates.wallet["read_pubkeys"]).fetchall())
    

    def WeSpend(self, tx):
        return CTx(tx).WeSpend()


    def isMineTx(self, tx):
        # Return True if we are reciptens of the given tx hash Else Return False 
        return self.IsMineKey(CTx(tx).GetRecipten()) or self.WeSpend(tx)
    
    def GetMyAddresses(self, addresses = []):
        # Return a list of wallet addresses 
        return [CKey().GetAddress(str(i)) for i in self.Read(self.templates.wallet["read_private_keys"]).fetchall()]
    
    def GetTxs(self):
        # Return a list of wallet transactions 
        return self.Read(self.templates.wallet["gettransactions"]).fetchall()
    
    def CountTxs(self):
        # Return the lenght of wallet transactions 
        return len(self.GetTxs())
    
    def AddTx(self, tx):
        # Add tx to wallet transactions 
        return self.Exec(self.templates.wallet["addtx"], [tx])


    def GetPriv(self, pub):
        f = self.Read(self.templates.wallet["getpriv"], [pub]).fetchone()[0]
        return f 



    def GetBalance(self):
        txs = {}
        balance = 0 
        if self.CountTxs() == 0:
            return balance
        # calculate balance  
        for transaction in self.GetTxs():
            if not CTx(transaction[0]).WeSpend():
                txs[transaction[0]] = CTx(transaction[0]).Value()
        
        # remove spended coins
        for transaction in self.GetTxs():
            if CTx(transaction[0]).WeSpend():
                txs[CTx(transaction[0]).Prev()] -= CTx(transaction[0]).Value() * COIN

        return float(sum(txs.values()) / COIN)


    def FindAddrFromHash(self, txhash):
        return self.GetPriv(CTx(txhash).GetRecipten())



    def FindHash(self, amount):

        # for each wallet tx 
        for transaction in self.GetTxs():
            # check if tx balancde is >= ampunt wich we want to spend
            if not CTx(transaction[0]).WeSpend():
                if CTx(transaction[0]).Value() >= amount * COIN and CTx(transaction[0]).IsReadyToSpend():
                    return transaction


    def GenerateTransaction(self, amount, recipten):
        mybalance = self.GetBalance()


        if len(recipten) != 130:
           # not vaild recipten key
           logg("GenerateTransaction() Failed not vaild recipten key")
           return False, "Failed not vaild recipten key"

        if mybalance < amount:
           # not enought balance to create this transaction
           logg("GenerateTransaction() Failed not enought balance to create this transaction")
           return False, "Failed not enought balance to create this transaction"

        if amount > nCoin:
            # Transactions currenlty supports one input to spend 
            # thats means that in a transaction cant be spend more than 50 coins 
            # wich is the initial block value 
            logg("GenerateTransaction() Cant spend more than 50 coins")
            return False, "Cant spend more than 50 coins"


        thisHash = self.FindHash(amount)
        
        if not thisHash:
            logg("GenerateTransaction() Coinbase maturity expected")
            return False, "Coinbase maturity expected"
            

        priv = self.FindAddrFromHash(thisHash[0])

        txNew = CTransaction()
        txNew.add("version", 1)
        txNew.add("prev_out", thisHash[0])
        txNew.add("time", int(time.time()))
        txNew.add("value", amount)
        txNew.input_script("SilmeTransaction")
        txNew.output_script(recipten)
        txNew.add("signature", ecdsa_sign(str(txNew),priv))

        if MemPool().AddTx(txNew):
            print "tx added to memppool"

        return True, "ok"


            


class CTx(CDB):
    def __init__(self, txhash, db = "blockchain.db"):
        self.self = CDB.__init__(self, db)
        self.txhash = txhash
    # CTx basic operations

    
    
    def Height(self):
        # Return the block height of the given tx hash
        return self.Read(self.templates.transactions["height"], [self.txhash]).fetchone()[0]
    
    def Version(self):
        # Return the Version of the given tx 
        return self.Read(self.templates.transactions["version"], [self.txhash]).fetchone()[0]
    
    def Time(self):
        # Return the Time of the given tx 
        return self.Read(self.templates.transactions["time"], [self.txhash]).fetchone()[0]

    def Prev(self):
        return self.Read(self.templates.transactions["prev"], [self.txhash]).fetchone()[0]

    
    def Value(self):
        # Return the Value of the given tx 
        return self.Read(self.templates.transactions["value"], [self.txhash]).fetchone()[0]
    
    def InsScript(self):
        # Return the Input Script of the given tx 
        return self.Read(self.templates.transactions["input_script"], [self.txhash]).fetchone()[0]
    
    def OutScript(self):
        # Return the Output script of the given tx 
        return self.Read(self.templates.transactions["output_script"], [self.txhash]).fetchone()[0]
    
    def isCoinbase(self):
        # Return True if this tx is coinbase False if not 
        return self.Read(self.templates.transactions["checkcoinbase"], [self.txhash]).fetchone()[0] == 0 
    
    def GetRecipten(self):
        # Return the recipten of tx 
        return self.OutScript().encode("hex_codec")[2:132]

    def GetSignature(self):
        # Return the signature of the given tx 
        return self.Read(self.templates.transactions["signature"], [self.txhash]).fetchone()[0]


    def WeSpend(self):
        if self.Prev() == 0:
            return False
        return True

    
    def IsReadyToSpend(self):
        # Check if a transaction can be spend 
        
        if not self.isCoinbase() or CBlockchain().getBestHeight() > self.Height() + COINBASE_MATURITY:
            return True
        elif CBlockchain().getBestHeight() < self.Height() + COINBASE_MATURITY:
            return False

    def GetSender(self):
        inputn = self.Prev()
        return CTx(inputn).GetRecipten()




class CBlockIndex(CDB):
    def __init__(self, obj, db = "blockchain.db"):
        self.self = CDB.__init__(self, db)
        self.block = obj
        if type(self.block) == int:
            self.height = self.block
            self.hash = self.Read(self.templates.cblockindex["gethashbyheight"], [self.block]).fetchone()[0]
            self.raw = self.Read(self.templates.cblockindex["getrawbyheight"], [self.block]).fetchone()[0]
            self.transactions = self.Read(self.templates.cblockindex["gettxsbyheight"], [self.block]).fetchall()
            if CBlockchain().getBestHeight() > 1:
                self.nonce = self.Read(self.templates.cblockindex["getnoncebyheight"], [self.block]).fetchone()[0]
        else:
            self.hash = self.block
            self.height = self.Read(self.templates.cblockindex["getheightbyhash"], [self.block]).fetchone()[0]
            self.raw = self.Read(self.templates.cblockindex["getrawbyhash"], [self.block]).fetchone()[0]
            self.transactions = self.Read(self.templates.cblockindex["gettxsbyhash"], [self.height]).fetchall()
            if CBlockchain().getBestHeight() > 1:
                self.nonce = self.Read(self.templates.cblockindex["getnoncebyhash"], [self.height]).fetchone()
    # CBlockIndex basic operations

    
    def Height(self):
        # Return block height 
        return self.height
    
    def Hash(self):
        # Return block hash 
        return self.hash
    
    def Raw(self):
        # Return block in hex format 
        return self.raw

    def Version(self):
        # Return block version 
        return decode_uint32(a2b_hex(self.raw[:8]))
    
    def Prev(self):
        # Return previous block hash 
        return self.raw[8:72]

    def Merkle(self):
        # Return block merkle root 
        return format_hash(a2b_hex(self.raw[72:136]))
    
    def Time(self):
        # Return block time 
        return decode_uint32(a2b_hex(self.raw[136:144]))
    
    def Bits(self):
        # Return block bits
        return decode_uint32(a2b_hex(self.raw[144:152]))
    
    def Nonce(self):
        # Return block nonce 
        return self.nonce
    
    def Txs(self):
        # Return block transactions 
        return self.transactions



class MemPool(CDB):
    def __init__(self, db = "mempool.db"):
        self.self = CDB.__init__(self, db)
        self.Exec(self.templates.mempool["transactions"])
    # MemPool basic operations


    def HaveHash(self, txhash):
        return txhash in self.Read(self.templates.mempool["getall"]).fetchall()

    def AddTx(self, tx):
        return self.Exec(self.templates.mempool["addtx"], (tx["version"], tx["prev_out"], tx["time"], tx["value"], hashlib.sha256(hashlib.sha256(str(tx)).hexdigest()).hexdigest(), tx["input_script"], tx["output_script"], tx["signature"]))

    
    def GetSize(self):
        # return mempool size in bytes 
        fsize = 0 
        mempool_txs = self.Read(self.templates.mempool["getall"]).fetchall()
        for tx in mempool_txs:
            fsize += sys.getsizeof(tx)
        return fsize

    def CountTxs(self):
        return len(self.Read(self.templates.mempool["getall"]).fetchall())

    def GetTx(self, n):
        return self.Read(self.templates.mempool["getall"]).fetchall()[n]

    def RemoveTx(self, tx):
        self.Exec(self.templates.mempool["removetx"], (tx.strip(),))

