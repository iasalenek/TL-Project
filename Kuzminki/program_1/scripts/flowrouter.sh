# Только входные
# python3 $SUMO_HOME/tools/detector/flowrouter.py --net-file Kuzminki/program_1/program_1.net.xml -d Kuzminki/detectors.xml  --routes-output Kuzminki/program_1/program_1.rou.xml --emitters-output Kuzminki/program_1/program_1.vehicles.rou.xml -f data/processed/program_1/101126.csv data/processed/program_1/101122.csv data/processed/program_1/15385.csv data/processed/program_1/10330.csv -i 5

# Все детекторы
# python3 $SUMO_HOME/tools/detector/flowrouter.py --net-file Kuzminki/program_1/program_1.net.xml -d Kuzminki/detectors.xml  --routes-output Kuzminki/program_1/program_1.rou.xml --emitters-output Kuzminki/program_1/program_1.vehicles.rou.xml -f data/processed/program_1/41039.csv data/processed/program_1/14171.csv data/processed/program_1/101126.csv data/processed/program_1/101122.csv data/processed/program_1/15385.csv data/processed/program_1/15186.csv data/processed/program_1/9568.csv data/processed/program_1/15059.csv data/processed/program_1/10330.csv -i 5

# Все детекторы с параметрами
python3 $SUMO_HOME/tools/detector/flowrouter.py --net-file Kuzminki/program_1/program_1.net.xml -d Kuzminki/detectors.xml  --routes-output Kuzminki/program_1/program_1.rou.xml --emitters-output Kuzminki/program_1/program_1.vehicles.rou.xml -f data/processed/program_1/41039.csv data/processed/program_1/14171.csv data/processed/program_1/101126.csv data/processed/program_1/101122.csv data/processed/program_1/15385.csv data/processed/program_1/15186.csv data/processed/program_1/9568.csv data/processed/program_1/15059.csv data/processed/program_1/10330.csv -i 5 --keep-det --random --lane-based

# sumo-gui -c Program1.sumocfg

