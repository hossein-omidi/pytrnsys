from pytrnsys.psim import processParallelTrnsys as pParallelTrnsys

pathBase = os.getcwd()

tool = pParallelTrnsys.ProcessParallelTrnsys()
tool.readConfig(pathBase, "process_pv_battery.config")
tool.process()
