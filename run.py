from Defect_analyzer_back.run_backend import start_backend
from Defect_analyzer_front.run_frontend import init_db, start_frontend


init_db()
start_backend()
start_frontend()
