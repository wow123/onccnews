echo Who am i:
whoami
echo Current dir:
pwd
echo DISPLAY=$DISPLAY
echo PATH=$PATH
echo HOME=$HOME
echo ONCC_HOME=$ONCC_HOME
date
python3 $ONCC_HOME/scrape_index.py
date
