import py_dss_interface

# Inicializa a interface do PyDSS
dss = py_dss_interface.DSSDLL()

# Define o alimentador e o caminho do arquivo
feeder = 'ULAD202'
dss.file = rf"C:\FeedersUdia\{feeder}\Master_{feeder}.dss"
# Compila o arquivo DSS
dss.text(f"compile {dss.file}")
# Resolve o circuito
dss.solution_solve()

dss.text("Buscoords coordenadasMT.dss")
dss.text("plot circuit Power max=2000 n n C1=$00FF0000")



