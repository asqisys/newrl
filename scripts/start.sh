git pull
git checkout p2p
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app/migrations/init_newrl.py
# cd migrations
# python migrate_chain.py
# python migrate_state.py
# cd ..
python app/p2p_main.py & app/python main.py
