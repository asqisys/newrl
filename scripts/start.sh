git pull
git checkout p2p
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.migrations.init
# cd migrations
# python migrate_chain.py
# python migrate_state.py
# cd ..
python -m app.main
