# newrl
This document describes the network behaviour in Newrl blockchain

1. newrl.net hosts the full list of active nodes
2. New joining node gets this full list from newrl.net
3. New node is suggested (by newrl.net) a subset of this list as its peers (10 or actual whichever is lesser)
4. The new node adds these peers to its own peer group and also calls add-peer on them to get added to their peer group
5. The bootstrap server (newrl.net) updates the network list for itself and broadcasts the new addition
