rm -rf engine
rm -rf metrics
mkdir engine
mkdir metrics
snips-nlu generate-dataset en base.yml > base.json
snips-nlu train base.json engine\\base