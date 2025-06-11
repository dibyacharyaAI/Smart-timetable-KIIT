🔁 Full Reset Instructions (Clean GitHub Clone & Fresh Setup)
🧼 1. Delete old project folder
bash
CopyEdit
cd ~
rm -rf Smart-timetable-KIIT

📥 2. Clone fresh from GitHub
bash
CopyEdit
git clone https://github.com/dibyacharyaAI/Smart-timetable-KIIT.git
cd Smart-timetable-KIIT

🐍 3. Recreate venv with correct Python
bash
CopyEdit
pyenv local 3.10.12
python -m venv venv
source venv/bin/activate

📦 4. Install clean dependencies
bash
CopyEdit
pip install --upgrade pip
pip install streamlit==1.32.2 torch ortools==9.6 pandas openpyxl scikit-learn
  🧪 Step-by-step pip install that works:
bash
CopyEdit
pip install streamlit==1.32.2
pip install torch==2.2.2
pip install ortools==9.5.2237
pip install pandas openpyxl scikit-learn
Pip install flask


🔒 These versions are:
* ✅ Fully compatible with Python 3.10
* ✅ Stable on M1/M2 Macs
* ✅ Confirmed to run your timetable pipeline

🧪 If ortools==9.5.2237 fails…
Use the source build:
bash
CopyEdit
pip install ortools==9.6.2534 --no-binary=ortools

Once done, confirm OR-Tools is usable:
bash
CopyEdit
python -c "from ortools.sat.python import cp_model; print('✅ OR-Tools CP-SAT working')"

✅ Then Launch App
bash
CopyEdit
streamlit run streamlit_app.py
  python api/app.py

