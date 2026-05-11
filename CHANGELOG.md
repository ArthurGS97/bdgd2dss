## [v0.0.9] - 08/05/2026

### 🚀 Novas Funcionalidades
- Adição automática do comando `CalcVoltageBases` no arquivo `Master.dss`.
- Atualização da modelagem dos `EnergyMeter`.
- Atualização da modelagem das chaves do circuito.
- Atualização nas rotinas auxiliares `exportar_qgis.py`.
- A rotina `loads_isolated.py` substituída por `elements_isolated.py`e melhoria neste código.

### 🐞 Correções
- Correção do dicionário de ligações do neutro.

## [v0.0.7] - 15/11/2025

### 🚀 Novas Funcionalidades
- Atualização do arquivo `exportar_qgis.py` para compatibilidade com qualquer versão da BDGD (antiga e nova).
- O arquivo `exportar_qgis.py` agora exporta apenas os dados necessários para a modelagem, reduzindo significativamente o tamanho dos arquivos e o tempo de simulação.
- Criação da rotina auxiliar `loads_isolated.py` para desconexão automática de cargas isoladas na modelagem.
- A rotina de testes de alimentadores foi transformada em módulo auxiliar (`test_feeders.py`), facilitando a manutenção e reutilização.
- A modelagem agora pode ser executada tanto na versão antiga quanto na nova da BDGD.
- Compatibilidade com **Python 3.14**.

### 🐞 Correções
- Correção de erro que causava modelagem incorreta em alimentadores numéricos.
- Todas as **chaves** agora são corretamente modeladas (antes, algumas eram ignoradas ou modeladas incorretamente).
- Correção na modelagem de reguladores de tensão.
- Correção de inconsistências de tipo de dado (`int`, `float`, `str`) em variáveis utilizadas na modelagem.
- A tentativa de modelar alimentadores inexistentes na BDGD analisada gerava erro; agora, uma mensagem de aviso é exibida e a modelagem prossegue normalmente.

