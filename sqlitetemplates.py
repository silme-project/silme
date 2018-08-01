#!/usr/bin/python
# Copyright (c) 2018 CVSC
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.



class Templates:


    blockchain = {"blocks": "CREATE TABLE IF NOT EXISTS blocks (height INTEGER, hash, raw, nonce)",
                  "transactions": "CREATE TABLE IF NOT EXISTS transactions (block, version, prev, time, value, hash, input_script, output_script, signature)",
                  "bestheight": "SELECT height from blocks",
                  "besthash": "SELECT hash FROM blocks",
                  "writeblock": "INSERT INTO blocks VALUES (?,?,?,?)",
                  "havehash": "SELECT hash FROM blocks",
                  "inserttx": "INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?)",
                  "getblock": "SELECT * FROM blocks where height = ?"}

    transactions = {"checkcoinbase": "SELECT prev FROM transactions WHERE hash = ?",
                    "height": "SELECT block FROM transactions WHERE hash = ?",
                    "version": "SELECT version FROM transactions WHERE hash = ?",
                    "time": "SELECT time FROM transactions WHERE hash = ?",
                    "prev": "SELECT prev FROM transactions WHERE hash = ?",
                    "value": "SELECT value FROM transactions WHERE hash = ?",
                    "input_script": "SELECT input_script FROM transactions WHERE hash = ?",
                    "output_script": "SELECT output_script FROM transactions WHERE hash = ?",
                    "signature": "SELECT signature FROM transactions WHERE hash = ?"}

    cblockindex = {"getrawbyheight": "SELECT raw FROM blocks WHERE height = ?",
                   "gethashbyheight": "SELECT hash FROM blocks WHERE height = ?",
                   "gettxsbyheight": "SELECT * FROM transactions where block = ?",
                   "getheightbyhash": "SELECT height FROM blocks WHERE hash = ?",
                   "getrawbyhash": "SELECT raw FROM blocks WHERE hash = ?",
                   "gettxsbyhash": "SELECT * FROM transactions where block = ?",
                   "getnoncebyhash": "SELECT nonce FROM blocks WHERE hash = ?",
                   "getnoncebyheight": "SELECT nonce FROM blocks WHERE height = ?"}

    wallet = {"keys": "CREATE TABLE  IF NOT EXISTS  keys (private, pubkey)", 
              "txs": "CREATE TABLE IF NOT EXISTS transactions (tx_hash)",
              "read_private_keys": "SELECT private from keys",
              "read_pubkeys": "SELECT pubkey from keys",
              "addkeys": "INSERT INTO keys VALUES (?,?)",
              "addtx": "INSERT INTO transactions VALUES (?)",
              "gettransactions": "SELECT tx_hash from transactions",
              "gettxsbyhash": "SELECT * FROM transactions where hash = ?",
              "getpriv": "SELECT private FROM keys where pubkey = ?"}

    mempool = {"transactions": "CREATE TABLE IF NOT EXISTS transactions (version, prev, time, value, hash, input_script, output_script, signature)",
               "getall": "SELECT * FROM transactions",
               "addtx": "INSERT INTO transactions VALUES (?,?,?,?,?,?,?, ?)",
               "removetx": "delete from transactions where hash=?"}
