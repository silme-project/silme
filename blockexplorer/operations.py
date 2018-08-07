from flask import jsonify
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from dboperations import *
from main import *
import datetime


def singleblockall(height):
    ppblocks = []

    blocks = {"height": CBlockIndex(height).Height(),
              "hash": CBlockIndex(height).Hash(),
              "age": int(time.time()) - CBlockIndex(height).Time(),
              "bits": CBlockIndex(height).Bits(),
              "txs": CBlockIndex(height).CountTxs(),
              "prev": CBlockIndex(height).Prev(),
              "merkle": CBlockIndex(height).Merkle(),
              "nonce": CBlockIndex(height).Nonce(),
              "version": CBlockIndex(height).Version(),
              "diff": str(CalculateDiff(CBlockIndex(height).Bits())),
              "time": datetime.datetime.fromtimestamp(CBlockIndex(height).Time()).strftime('%Y-%m-%d %H:%M:%S')

            }

    ppblocks.append(blocks)

    return ppblocks


def blocktxs(height):
    ttxs = []
    txs = CBlockIndex(height).Txs()
    for tx in txs:
        txhash = tx[5]

        sender = ""
        if CTx(tx[5]).isCoinbase():
            sender = "coinbsase"
        else:
            sender = CTx(tx[5]).GetSender()



        tx = {"hash": tx[5],
              "prev": CTx(tx[5]).Prev(),
              "value": CTx(tx[5]).Value(),
              "recipten": CTx(tx[5]).GetRecipten(),
              "inputscript": CTx(tx[5]).InsScript().encode("hex"),
              "outputscript": CTx(tx[5]).OutScript().encode("hex"),
              "sender": sender,
              "type": CTx(tx[5]).GetType()}

        ttxs.append(tx)
    return ttxs


def singletx(txhash):
    ttx = []
    sender = ""
    if CTx(txhash).isCoinbase():
        sender = "coinbsase"
    else:
        sender = CTx(txhash).GetSender()



    tx = {"hash": txhash,
          "prev": CTx(txhash).Prev(),
          "value": CTx(txhash).Value(),
          "recipten": CTx(txhash).GetRecipten(),
          "inputscript": CTx(txhash).InsScript().encode("hex"),
          "outputscript": CTx(txhash).OutScript().encode("hex"),
          "sender": sender,
          "type": CTx(txhash).GetType()
          }

    ttx.append(tx)

    return ttx



def getblocksall():
    blocks = []

    for x in xrange(1, CBlockchain().getBestHeight() +1):
        theight = CBlockIndex(x).Height()
        thash = CBlockIndex(x).Hash()
        tage = int(time.time()) - CBlockIndex(x).Time()
        ctxs = CBlockIndex(x).CountTxs()

        block = {"height": theight,
                 "hash": thash,
                 "age": tage,
                 "transactions": ctxs}

        blocks.append(block)

    return blocks






def getblocksfront():

	blocks = []

	from_ = 1

	stop = CBlockchain().getBestHeight() +1


	while from_ < stop:
		theight = CBlockIndex(from_).Height()
		thash = CBlockIndex(from_).Hash()
		tage = int(time.time()) - CBlockIndex(from_).Time()
		ctxs = CBlockIndex(from_).CountTxs()

		block = {"height": theight,
		         "hash": thash,
		         "age": tage,
		         "transactions": ctxs}

		blocks.append(block)

		from_ +=1
	return blocks


def GetBlock(i):
    
    return jsonify(
        height=CBlockIndex(i).Height(),
        hash=CBlockIndex(i).Hash(),
        prev=CBlockIndex(i).Prev(),
        merkle=CBlockIndex(i).Merkle(),
        time=CBlockIndex(i).Time(),
        bits=CBlockIndex(i).Bits(),
        txs=len(CBlockIndex(i).Txs())
    )


def getTransaction(i):


    # first be sure that have this tx
    try:
        version = CTx(i).Version()
    except Exception as e:
        return jsonify("null")
    else:
        pass

    sender = ""

    if CTx(i).isCoinbase():
        sender = "coinbsase"
    else:
        sender = CTx(i).GetSender()


    return jsonify(
        height=CTx(i).Height(),
        hash=i,
        
        prev=CTx(i).Prev(),
        time=datetime.datetime.fromtimestamp(int(CTx(i).Time())).strftime('%Y-%m-%d %H:%M:%S'),
        value=CTx(i).Value(),
        recipten=CTx(i).GetRecipten(),
        inputscript= CTx(i).InsScript().encode("hex"),
        outputscript= CTx(i).OutScript().encode("hex"),
        sender=sender
    )


def GetBalance(i):
	# return the balance of the given key 
	return str(CBlockchain().GetBalance(i))


def GetTxs(i):
	# return all txs from the given key 
	return jsonify(CBlockchain().GetTxsByKey(i))

