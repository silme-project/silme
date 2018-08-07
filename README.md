# Silme

### What is silme ?

A simple implementation of p2p cryptoccurency Blockchain writen in python

### What i can do with silme ?

- Using silme anyone can mine new blocks and generate new coins 
- Using silme anyone can receive and send coins to any vaild silme key

### Limitations 

Curently silme transaction use 1 input, that means in a transaction can't be spend more than 50 coins wich that is the initial block reward value, so if bob wants to send to alice 200 coins need to make 4 transactions to alice with 50 coins per transaction @ Need fix 

### Peer-to-Peer (p2p)

Since this is a peer-to-peer network, every instance has to be both the a server and a client, both server and client starts with silme-qt, server runs under defaults [p2p] at silme.conf


 -   Boostrap by way of a preconfigured list
 -   Connect to other nodes and make a handshake.
 -   Ask peers for nodes and connect to them
 -   Ask peers if sync needed 
 -   Sync with peers if needed
 -   Ping peers
 -   Send new mined blocks to other peers
 -   Validate transactions and pass it to other peers 




# Discussion 

http://t.me/Csilme

## TODO

You can contribute to silme, simple open a pull request 

# RUN SILME 
``` bash
cd silme
./configure
./silme-qt
```
![Alt text](http://i65.tinypic.com/wirl29.jpg?raw=true "Title")

# USAGE

# RPC

Silme supports rpc commands
Using rpc 
``` bash
./silmed start - Start rpc server
./silmed stop - Stop rpc server

./silmed help - Get a list of the available commands

--------------   Blockchain --------------

getbestheight - Reurn the best height in the longest chain
getbesthash - Reurn the best hash in the longest chain
getdifficulty - Reurn the current difficulty
nethashrate - Reurn the current networkhashrate in ghs
getinfo - Reurn info about wallet && Blockchain

--------------  Wallet --------------

getbalance - Return wallet balance
getnewaddress - Reurn a new bitcoin address
getmyaddresses - Return a list of addresses

--------------  Mining --------------
mempoolcount - Return mempool transactions count
gettarget - Return the pow target
-------------------------------------
version - Return silme version


```

# RUN BLOCK EXPLORER
``` bash
cd silme 
./configure
cd blockexplorer
python explorer.py
```
Block explorer is build in top of flask, block explorer allows you to view information about blocks, addresses, and transactions on the Silme blockchain, block explorer runs under default port 4989, in order to keep block explorer updated with blockchain first need to run silme-qt..

![Alt text](http://i64.tinypic.com/nnqvya.png?raw=true "Title")





## MINING

Start Mining using the start button in mining section in silme-qt, when you will find a vailid block you will credit the coinbase transaction value, to stop mining click the stop button in mining section, alternative for testing purposes you can use ./miner -d 1 to enable mining with debug results should be 
``` bash

[*] Working on block: 2
[*] Target: 110427836236357352041769395878404723568785424659630784333489133269811200
[*] Difficulty: 0.000244137132537
[*] Required hashes: 1048577.0
[*] Prev hash: 000009cb25c348b85b01819c52402adea224580263fbe9b915be8502c5220f82
```

## SEND COINS

Send coin section take 2 arguments, first to: the recipten pubkey and and second anount: the amount wich you want to sent to argument 1 pubkey

# DEVELOPMENT DOCUMANTATION

## keys, CKey is located at main 

``` python
CKey().MakeNewKey() # Generate a new private key 
CKey().GetPubKey(priv) # Get pubkey of the given private key 
CKey().GetAddress(pubkey) # Get address of the given pubkey

```

## CWalletDB() is located at dboperations

``` python
CWalletDB().WriteKey(key, pubkey) # Write a private key and their pubkey to wallet db
CWalletDB().IsMineKey(pubkey) # Return True if the give pubkey is in wallet
CWalletDB().WeSpend(tx_hash) # Return True if the give tx hash include our tx as input
CWalletDB().isMineTx(tx_hash) # Return True if tx hash is our False if not 
CWalletDB().GetMyAddresses() # Return a list of addresses from our wallet
CWalletDB().GetTxs() # Return a list of wallet transactions 
CWalletDB().CountTxs() # Return the lenght of wallet transactions
CWalletDB().AddTx(tx_hash) # Add tx hash to wallet transactions 
CWalletDB().GetPriv(pubkey) # Return the privatekey of the given public key
CWalletDB().GetBalance() # Return wallet balance
CWalletDB().FindAddrFromHash(tx_hash) # Return the privatekey of the tx_hash output
CWalletDB().FindHash(amount) # Return a tx hash to use as input for a new transaction, tx hash must have the specified amount
CWalletDB().GenerateTransaction(amount, recipten) # Generate a new transaction


```

## CBlockIndex() is located at dboperations

``` python
CBlockIndex() # Return info of the give blockhash or height
CBlockIndex(@HashOrHeight).Version() # Return @HashOrHeight version
CBlockIndex(@HashOrHeight).Prev() # Return @HashOrHeight previous block hash 
CBlockIndex(@HashOrHeight).Merkle() # Return @HashOrHeight merkle root 
CBlockIndex(@HashOrHeight).Time() # Return @HashOrHeight time 
CBlockIndex(@HashOrHeight).Bits() # Return @HashOrHeight bits 
CBlockIndex(@HashOrHeight).Nonce() # Return @HashOrHeight nonce 
CBlockIndex(@HashOrHeight).Txs() # Return @HashOrHeight transactions 

```

## CTx() is located at dboperations

``` python
CTx() # Return info of the give transaction hash
CTx(@tx_hash).Height() # Return the height of block of the give tx_hash
CTx(@tx_hash).Version() # Return @tx_hash version 
CTx(@tx_hash).Time() # Return @tx_hash time 
CTx(@tx_hash).Prev() # Return txhash of the input hash 
CTx(@tx_hash).Value() # Return @tx_hash value
CTx(@tx_hash).InsScript() # Return @tx_hash input_script 
CTx(@tx_hash).OutScript() # Return @tx_hash output_script 
CTx(@tx_hash).isCoinbase() # Return True if tx is coinbase False if not 
CTx(@tx_hash).GetRecipten() # Return @tx_hash recipten pubkey 
CTx(@tx_hash).IsReadyToSpend() # Return True if is not coinbase, Return True or False if pass coinbase majurity
CTx(@tx_hash).GetSender() # Return the sender pubkey 
```

## CBlockchain() is located at dboperations

``` python
CBlockchain() # Return info about blockchain
CBlockchain().getBestHeight() # Return the best height in the blockchain
CBlockchain().GetBestHash() # Return the best hash in the blockchain
CBlockchain().haveHash(@hash) # Return True if the give hash already exists False if not
CBlockchain().GetBalance(@pubkey) # Return the balance of the given pubkey 

```
