git pull
git checkout p2p
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_newrl.py
cd migrations
python migrate_chain.py
python migrate_state.py
cd ..
python p2p_main.py & python main.py
