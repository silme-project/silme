# Silme

A simple implementation of Blockchain writen in python, using silme you can generate new blocks (pow sha256) and create transactions, node is not implemented yet so the new transactions and blocks cant be broadcasted to other peers

# Discussion 

http://t.me/Csilme

## TODO

You can contribute to silme, simple open a pull request 

# RUN SILME 
``` bash
cd silme
./silme-qt
```

# USAGE

# RPC

Silme supports rpc commands
``` bash
./silmed start - Start rpc server
./silmed stop - Stop rpc server
./silmed help - Get a list of the available commands
```

## MINING

Start Mining using the start button in mining section, when you will find a vailid block you will credit the coinbase transaction value, to stop mining click the stop button in mining section, alternative for testing purposes you can use ./miner -d 1 to enable miining with debug results should be 
``` bash

[*] Working on block: 2
[*] Target: 110427836236357352041769395878404723568785424659630784333489133269811200
[*] Difficulty: 0
[*] Required hashes: 0
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

## Wallet, CWalletDB is located at dboperations

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

