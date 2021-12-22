# newrl
This document describes the network behaviour in Newrl blockchain

1. newrl.net hosts the full list of active nodes
2. New joining node gets this full list from newrl.net
3. New node is suggested (by newrl.net) a subset of this list as its peers (10 or actual whichever is lesser)
4. The new node adds these peers to its own peer group and also calls add-peer on them to get added to their peer group
5. The bootstrap server (newrl.net) updates the network list for itself and broadcasts the new addition to all (including non-peers)

Peer list maintenance
1. While broadcasting, if a node X realizes that a specific peer is non-responsive, it removes it from the active peer list.
2. The removed node will have to call add-peer again for communicating with node X.
3. The removed node can also rejoin afresh as per the above new node process, espcially if it finds itself removed from active peer list by most of its erstwhile peers

Gossip protocol is the primary mode of transmitting messages across the network. In the early days, all nodes are direct peers of everyone else. So gossip defaults to simple broadcast.
Transaction Broadcast
1. Each transaction is broadcasted by its creator node to its peers
2. Peers validate the transaction and if found valid, send it to their peers (other than the one that sent them the tx)
3. Peers recieve transaction only if they don't already have it

Block broadcast
1. The selected node for minting a block sends it to its peers - including its signature for the block.
2. The contents of the block that are sent include only transaction ids and not the full transactions.
3. However, transaction hash included in the header the block is that of entire transactions.
4. Peers receive blocks only if they don't already have it

Local update by peers upon receiving a block
1. Each peer that receives a block, first checks if the signature is valid and that the sending node was in fact selected to mint the block
2. If yes, the receiving peer does the following
    a. Validates all transactions in the received block, locally. If one or more transactions are invalid, ignores the block.
    b. If all transactions are valid, updates its own chain by including the transactions from the mempool for the transaction ids corresponding to those in the received block
    c. Deletes included transactions from the mempool
    d. Modifies its local state using the transactions included in the new block
3. If the block is valid and processed as per the above logic, each peer sends it onwards to its peers excluding the one that sent it
