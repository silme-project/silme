#!flask/bin/python

from flask import Flask
from flask import render_template
from flask import abort
from flask import request

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from dboperations import *
from operations import *




app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False

@app.route('/')
def index():
    # index main page show only last 5 blocks 
    lastblocks = getblocksfront()
    return render_template('index.html', object_list=lastblocks[::-1])


@app.route('/api')
def api():
    # api
    lastblocks = getblocksfront()
    return render_template('api.html', object_list=lastblocks[::-1])


@app.route('/data/allblocks')
def allblocks():
    # allblocks main page show all blocks 
    txs_list = getblocksall()
    return render_template('allblocks.html', object_list=txs_list[::-1])






@app.route('/data/block/<row_id>/')
def detail(row_id):
    object_list = getblocksfront()
    for row in object_list:
        if row['height'] == int(row_id):
            return render_template("data_block.html", object=singleblockall(int(row_id)))
    abort(404)


@app.route('/search/')
def search():
    data = request.args['info']

    # check if is blockhash
    if len(data) == 64 and CBlockchain().haveHash(data):
        return render_template('data_block.html', object = singleblockall(CBlockIndex(data).Height()))

    # check if tx
    elif len(data) == 64:
        tx = getTransaction(data)
        if tx and tx != "null":
            return tx

    # check if key 

    else:
        return abort(404)



@app.route('/api/block/<string:block_hash>', methods=['GET'])
def get_block_by_hash(block_hash):
    if CBlockchain().haveHash(block_hash):
        return GetBlock(block_hash)
    return jsonify("null")


@app.route('/api/rawblock/<string:block_hash>', methods=['GET'])
def get_rawblock_by_hash(block_hash):
    if CBlockchain().haveHash(block_hash):
        return str(CBlockIndex(block_hash).Raw())
    return jsonify("null")


@app.route('/api/block-index/<int:block_id>', methods=['GET'])
def get_block_by_index(block_id):
    if block_id <= CBlockchain().getBestHeight():
        thishash = CBlockIndex(block_id).Hash()
        data = {"blockHash": thishash}
        return jsonify(data)
    return jsonify("null")


@app.route('/api/tx/<string:tx_id>', methods=['GET'])
def gettransactiona(tx_id):
    return getTransaction(tx_id)


@app.route('/api/txs/<string:pubkey>', methods=['GET'])
def get_txs(pubkey):
    return GetTxs(pubkey)


@app.route('/api/balance/key/<string:pubkey_id>', methods=['GET'])
def get_balance(pubkey_id):
    return GetBalance(pubkey_id)


if __name__ == '__main__':
    app.run(debug=True, port=4989)