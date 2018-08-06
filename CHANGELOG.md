# Changelog
All notable changes to this project will be documented in this file after [commit](https://github.com/silme-project/silme/commit/328ec6c7afc90809e3a3fc18b32a80e6e0a042e5)

## v-0.0.3-beta 

- Added coinbase maturity, coinbase transactions need 4 blocks before them can be spent 
- Added showtxs.py, A simple GUI tool to explorer wallet transactions
- GUI GenerateTransaction returns Response
- Added protocol version (p2p)
- GUI confirm exit && stop (p2p)
- Removed unused code
- Fix typos 

## v-0.0.2-beta

- Blockchain sync works without need to restart the client
- More logging instead of print in network.py 
- Default p2p host, port added to config file 
- Node now reads default p2pport and p2phost from config file 
- Added clear.sh, recursively removes all .pyc files
- ./configure is now required before any action, because node needs config file to read data 
- Removed some local nodes from bootstrap_nodes.py
