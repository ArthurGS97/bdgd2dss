<!-- References (Formatting): -->
<!-- https://portal.revendadesoftware.com.br/manuais/base-de-conhecimento/sintaxe-markdown -->
<!-- https://docs.github.com/en/enterprise-cloud@latest/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax -->

# bdgd2dss

Conjunto de arquivos referente a biblioteca **bdgd2dss** desenvolvida na linguagem *Python*, que transforma as planilhas oriundas da Base de Dados Geográfica da Distribuidora (BDGD) em arquivos *.dss* para simulação e estudos de alimentadores de sistemas de distribuição de energia elétrica no ambiente *OpenDSS*. A ferramenta em questão foi criada pelo Mestrando em Engenharia Elétrica Arthur Gomes de Souza que desenvolve pesquisas com o foco em proteção de sistemas elétricos de potência, sob orientação do prof. Dr. Wellington Maycon Santos Bernardes (Universidade Federal de Uberlândia).


## 1 - Base de Dados Geográfica da Distribuidora - BDGD

A BDGD faz parte integrante do Sistema de Informação Geográfico Regulatório da Distribuição (SIG-R). Em adição, é um modelo geográfico estabelecido com o objetivo de representar de forma simplificada o sistema elétrico real da distribuidora, visando refletir tanto a situação real dos ativos quanto as informações técnicas e comerciais de interesse. De forma a emular a rede elétrica dos agentes envolvidos, a BDGD é estruturada em entidades, modelos abstratos de dados estabelecidos com o objetivo de representar informações importantes, como as perdas estimadas pelos agentes. Cada uma dessas entidades é detalhada em diversos dados, dentre as quais constam aquelas que devem observar a codificação pré-estabelecida pelo Dicionário de Dados da Agência Nacional de Energia Elétrica (ANEEL) (DDA), o qual especifica padrões de dados a serem utilizados na BDGD, visando a normalização das informações. Em relação aos dados cartográficos, eles são disponibilizados em um arquivo *Geodatabase* (*.gdb*), por distribuidora. O Manual de Instruções da BDGD (https://www.gov.br/aneel/pt-br/centrais-de-conteudos/manuais-modelos-e-instrucoes/distribuicao) e o Módulo 10 do PRODIST (https://www.gov.br/aneel/pt-br/centrais-de-conteudos/procedimentos-regulatorios/prodist) contém informações úteis para entender a BDGD, como as entidades disponibilizadas e as definições dos campos. 

Inicialmente, os dados da BDGD são classificados como entidades geográficas e não geográficas, as Tabelas 1 e 2 mostram as camadas que as compõe, respectivamente.


**Tabela 1: Entidades geográficas da BDGD.** 
| id  | Sigla  | Nome                                                       |
|-----|--------|------------------------------------------------------------|
| 22  | ARAT   | Área e Atuação                                             |
| 23  | CONJ   | Conjunto                                                   |
| 24  | PONNOT | Ponto Notável                                              |
| 25  | SSDAT  | Segmento do Sistema de Distribuição de Alta Tensão         |
| 26  | SSDBT  | Segmento do Sistema de Distribuição de Baixa Tensão        |
| 27  | SSDMT  | Segmento do Sistema de Distribuição de Média Tensão        |
| 28  | SUB    | Subestação                                                 |
| 38  | UNCRAT | Unidade Compensadora de Reativo de Alta Tensão             |
| 29  | UNCRBT | Unidade Compensadora de Reativo de Baixa Tensão            |
| 30  | UNCRMT | Unidade Compensadora de Reativo de Média Tensão            |
| 39  | UCAT   | Unidade Consumidora de Alta Tensão                         |
| 40  | UCBT   | Unidade Consumidora de Baixa Tensão                        |
| 41  | UCMT   | Unidade Consumidora de Média Tensão                        |
| 42  | UGAT   | Unidade Geradora de Alta Tensão                            |
| 43  | UGBT   | Unidade Geradora de Baixa Tensão                           |
| 44  | UGMT   | Unidade Geradora de Média Tensão                           |
| 31  | UNREAT | Unidade Reguladora de Alta Tensão                          |
| 32  | UNREMT | Unidade Reguladora de Média Tensão                         |
| 33  | UNSEAT | Unidade seccionadora de Alta Tensão                        |
| 34  | UNSEBT | Unidade seccionadora de Baixa Tensão                       |
| 35  | UNSEMT | Unidade seccionadora de Média Tensão                       |
| 36  | UNTRD  | Unidade Transformadora da Distribuição                     |
| 37  | UNTRS  | Unidade Transformadora da Subestação                       |

**Fonte:** Adaptado de ANEEL (2021).

**Tabela 1: Entidades não geográficas da BDGD.**

| id  | Sigla   | Nome                                          |
|-----|---------|-----------------------------------------------|
| 3   | BE      | Balanço de Energia                            |
| 0   | BAR     | Barramento                                    |
| 1   | BASE    | Base                                          |
| 2   | BAY     | _Bay_                                         |
| 4   | CTAT    | Circuito de Alta Tensão                       |
| 5   | CTMT    | Circuito de Média Tensão                      |
| 6   | EP      | Energia Passante                              |
| 7   | EQCR    | Equipamento Compensador de Reativo            |
| 8   | EQME    | Equipamento Medidor                           |
| 9   | EQRE    | Equipamento Regulador                         |
| 10  | EQSE    | Equipamento Seccionador                       |
| 11  | EQSIAT  | Equipamento do Sistema de Aterramento         |
| 12  | EQTRD   | Equipamento Transformador da Distribuição     |
| 13  | EQTRM   | Equipamento Transformador de Medida           |
| 14  | EQTRS   | Equipamento Transformador da Subestação       |
| 15  | EQTRSX  | Equipamento Transformador do Serviço Auxiliar |
| 16  | INDGER  | Indicadores Gerenciais                        |
| 18  | PNT     | Perdas não Técnicas                           |
| 19  | PT      | Perdas Técnicas                               |
| 17  | PIP     | Ponto de Iluminação Pública                   |
| 20  | RAMLIG  | Ramal de Ligação                              |
| 21  | SEGCON  | Segmento Condutor                             |

**Fonte:** Adaptado de ANEEL (2021).

### 1.2 - *Download* dos arquivos

Para realizar o *download* dos dados de uma distribuidora, basta acessar o link: https://dadosabertos-aneel.opendata.arcgis.com/search?tags=distribuicao e pesquisá-la. Assim sendo, aparecerá mais de um arquivo, correspondente a cada ano. A Figura 1 mostra essa etapa.

![dadosabertos_f1](https://github.com/user-attachments/assets/7a004291-d5ac-41c0-a7e1-31eacc8aa05d)

**Figura 1: Captura de tela dos dados da BDGD.**

**Fonte:** ANEEL (2024).

Escolhendo o arquivo correspondente, basta baixar como mostra a Figura 2. Alerta-se que essa etapa pode demorar um pouco. 

![download_f2](https://github.com/user-attachments/assets/0af2394f-d911-43b9-bba1-208eba72b2da)

**Figura 2: Captura de tela de *download* dos dados da BDGD.**

**Fonte:** Adaptado de ANEEL (2024).

## 2 - Tratamento dos arquivos no *QGIS*

### 2.1 - Gerenciador de Fonte de Dados

Após realizado o *download*, será possível trabalhar com os arquivos. Para isso deve-se usar a ferramenta *QGIS*, um *software* livre com código-fonte aberto, e multiplataforma. Basicamente é um sistema de informação geográfica (SIG) que permite a visualização, edição e análise de dados georreferenciados. O *download* pode ser feito no *link*: https://qgis.org/download/. Abrindo o *QGIS*, deve-se ir em "Gerenciador da Fonte de Dados" (opção Vetor). Ao selecionar a opção "Diretório", coloca-se a codificação em "Automático", em Tipo escolhe-se a opção "Arquivo aberto GDB", e em Base de Vetores escolhe a pasta do arquivo BDGD baixado e extraído. Finalmente em *LIST_ALL_TABLES* coloca-se em "*YES*" para ser possível uma pré-visualização das camadas disponíveis e selecionar aquelas que desejar visualizar. Essa etapa é mostrada na Figura 3  . 

![fontededados_f3](https://github.com/user-attachments/assets/9bef0b68-8487-4a55-bae3-45ec3012fcf5)

**Figura 3: Captura de tela do carregamento dos dados no *QGIS*.**

**Fonte:** O autor (2024).

### 2.2 - Escolha das Camadas

Já na Figura 4 são mostradas as camadas das Tabelas 1 e 2. Selecione aquelas com realce em azul, são elas: CRVCRG, CTMT, EQTRAT, EQTRMT, PIP, RAMLIG, SEGCON, SSDBT, SSDMT, SUB, UCBT, UCMT, UGBT, UGMT, UNCRMT, UNSEMT, UNTRAT e UNTRMT. Elas serão utilizadas para a realização da modelagem dos alimentadores. 

![tabelacamadas_f4](https://github.com/user-attachments/assets/93f402db-9ddf-4d44-8833-91cf1d1241b0)

**Figura 4: Captura de tela do *QGIS* mostrando as camadas da BDGD**

**Fonte:** O Autor (2024).

### 2.3 - Escolha da Zona Específica a Ser Estudada

Para otimizar as simulações e reduzir a quantidade de dados, é recomendável focar em uma área / região / zona específica, em vez de utilizar todos os dados da distribuidora. Por exemplo, pode-se escolher um município, como Uberlândia - Minas Gerais (ou outro à escolha do usuário), e trabalhar apenas com as informações dessa cidade. Para isso, é necessário filtrar as camadas, mantendo apenas os dados relevantes ao município. Uma maneira eficaz de fazer isso é identificar as subestações correspondentes e realizar o filtro em todas as camadas, já que todas possuem o atributo referente a uma subestação (SE). Para localizar as subestações e obter o código correspondente, clique com o botão direito na camada das SEs, e selecione a opção "Abrir tabela de atributos". A Figura 5 mostra essa etapa.

![atributos_f5](https://github.com/user-attachments/assets/e8aff2fb-a32f-438a-975a-f0d994fecf75)

**Figura 5: Captura de tela do *QGIS* para abrir a Tabela de Atributos.**

**Fonte:** O Autor (2024).

Com a Tabela de atributos aberta, deve-se localizar as subestações de Uberlândia (município escolhido para a realização dos testes), e salvar os COD_ID delas, como mostra a Figura 6 em sequência.

![SEs_f6](https://github.com/user-attachments/assets/915d960b-1f56-458a-a3a4-5344a1a0d610)

**Figura 6: Captura de tela do *QGIS* pra identificação das subestações**

**Fonte:** O Autor (2024).

### 2.4 - Filtragem das Camadas e Exportando Planilhas

Com essa informação, agora será possível ir em todas as camadas e realizar a filtragem. Para tal, ao clicar com o botão direito do mouse, escolha a opção "Filtrar", aparecerá uma caixa de texto que deve ser escrita seguindo uma lógica simples de programação para realizar o filtro. A Figura 7 mostra essa etapa.

![filtrar_f7](https://github.com/user-attachments/assets/29b8f9f6-6d7d-4363-88bd-8dfce0b03dcb)

**Figura 7: Captura de tela do *QGIS* do processo de filtragem das camadas.**

**Fonte:** O Autor (2024).

Em sequência, repete-se o processo para todas as outras camadas. Deve-se copiar o filtro anterior e aplicar para todas as camadas que tem o atributo SUB. Assim, finalmente, pode-se fazer a exportação de todas as camadas para arquivos *.csv*, que serão utilizadas no arquivo *Python* para a modelagem do alimentador. Com o botão direito do *mouse*, sobre a camada, vá na opção "Exportar" -> "Guardar elementos como...". A seguir, selecione o formato desejado (*.csv*), o local que deseja salvar e desmarque a opção "Adicionar arquivo salvo ao mapa". É aconselhável que dentro da mesma pasta que foi salvo o arquivo *bdgd2dss* (e outros *scripts* que serão citados), crie-se uma pasta chamada "*Inputs*" e salve as exportações que forem realizadas dentro do *QGIS* de todas as camadas. A Figura 8 mostra esse processo.

![exportar_f8](https://github.com/user-attachments/assets/859c9268-d8b1-43bb-a9db-be0b84fe3d01)

**Figura 8: Captura de tela do *QGIS* do processo exportação das camadas em arquivos *.csv***

**Fonte:** O Autor (2024).

<!-- Explique aqui sobre "Adicionar arquivo salvo ao mapa"-->
> [!WARNING]
> Se "Adicionar arquivo salvo ao mapa" for selecionado, então...

Para exportar as coordenadas das barras, o processo é um pouco diferente. Deve-se abrir a Tabela de Atributos da camada SSDMT. A seguir, é adequado esperar carregá-la, visto que pode demorar um pouco. A seguir, aperte as teclas *CTRL*+A (selecionando todos os dados), aperte *CTRL*+C, e cole esses dados numa planilha *.xlsx*. As Figuras 9 e 10 mostram essas etapas.

![atributos_coordenadas](https://github.com/user-attachments/assets/2c9822c7-29f5-461b-ae2d-845b22050c08)

**Figura 9: Captura de tela do *QGIS* do processo de copiar os dados da camada SSDMT para gerar posteriormente as coordenadas**

**Fonte:** O Autor (2024).

![coordenadasplanilha](https://github.com/user-attachments/assets/7dd8f421-4d99-4c9f-8a2a-bd75b3beda8d)


**Figura 10: Captura de tela do *QGIS* do processo de colar os dados da camada SSDMT para gerar posteriormente as coordenadas**

**Fonte:** O Autor (2024).

Agora é só salvar a planilha em arquivo *.csv* dentro do próprio *Microsoft Excel*, sendo na mesma pasta dos arquivos que foram exportados anteriormente.

! OBS: Há outras maneiras de trabalhar com esses dados sem utilizar o *QGIS*, e direcionando as informações diretamente para o *Python*, mas usando o *QGIS*, o processo demonstrou bem mais eficiente e rápido. 

Finalizado o processo de exportação das camadas, agora pode-se ir para os *scripts* em *Python* que realizarão a modelagem de alimentadores, verificação de convergência e validação dos mesmos.

## 3 - Convertendo BDGD em *.dss* usando *Python*

Para auxiliar o usuário foi disponibilizada uma rotina que lista os alimentadores presentes nos arquivos. O *script* se chama feeders.py e está aqui nesse diretório. Corresponde a primeira função presente no código. Com os dados baixados, agora é possível utilizar o *bdgd2dss* e modelar os alimentadores desejados. Para que possa criar os arquivos *.dss* necessários para a simulação deste, o único dado de entrada no programa *bdgd2dss* é o nome do alimentador e o dia de análise (DU - Dia útil, SA - Sábado e DO - Domingo). {c:red}MELHORAR: Salienta-se que foi criado um *script* que chama a biblioteca *bdgd2dss* e escolhe se os alimentadores que serão modelados, está também aqui no diretório e se chama gerarali.py, nele que será colocado os dados de entrada citados.{\c}

Inicialmente sugere-se ao usuário escolher uma gama de alimentadores para que possa ser verificado quais estão adequados. A Figura 11 mostra esse procedimento, onde será modelado todos os alimentadores de cidade de Uberlândia-MG.

![f9_codigogerar_ali](https://github.com/user-attachments/assets/e513bddb-9a9a-4a6c-ad4b-22244f9baa31)

**Figura 11: Captura de tela do Visual Code do códifo gerarali.py sendo utilizado**

**Fonte:** O Autor (2024).

A título de demonstração de desempenho computacional, usou-se uma máquina que possui as seguintes configurações: *8th Gen Intel (R) Core (TM) i5-8500 @3.00GHz; 8 GB RAM; Windows 10 Pro and SSD NVMe*. O procedimento demorou 2822 segundos, que são aproximadamente 47 minutos, para gerar a modelagem dos 62 alimentadores da cidade de Uberlândia - Minas Gerais.

Em sequência utiliza-se a segunda função do *script* nomeada *feeders.py*. Esse criará uma planilha listando os alimentadores, quais convergem, e, também, uma análise da diferença de energia medida a partir dos dados da camada *CTMT* comparados com aqueles da simulação no OpenDSS, ao longo de um ano. Desta forma, o usuário poderá escolher um alimentador mais adequado, pois devido a falta de informações ou inconsistências na criação das planilhas da *BDGD* e disponibilização no repositório, acarretando, portanto, em erros na modelagem.A Figura 12 mostra essa planilha gerada. Um limiar de 15% foi escolhido entre as medidas de energia, no intuito de considerar que o alimentador está adequado ou não para análises e estudos. 

![planilhafeeders](https://github.com/user-attachments/assets/a7abef38-c0c1-4d13-8f5c-d2d91f0b737f)

**Figura 12: Captura de tela do planilha gerada em *feeders.py* para escolha do alimentador baseado na convergência e limiar adotados**

**Fonte:** O Autor (2024).

Com o alimentador escolhido, o usuário poderá direcionar para as suas análises e estudos. Algo importante a ser comentado é que para simular o alimentador, deve-se entrar no arquivo *Master* dele, e colocar o *solve* no fim do arquivo, e o arquivo das coordenadas para ser possível visualizar o circuito dentro do *OpenDSS*. Essa tarefa pode ser feita dentro do *OpenDSS* ou no ambiente *Python* com o auxilio da biblioteca *pydss*, que inclusive já foi utilizada anteriormente nos códigos. No diretório foi disponibilizada uma rotina para simular o alimentador e colher os dados desejados, chamado *solvedss.py*. o usuário apenas deverá entrar com o nome do alimentador em questão. Por fim, a Figura 13 mostra parte desse código. 

![solvedss](https://github.com/user-attachments/assets/124d9dae-863a-4cef-9277-c04ffb378fdb)

**Figura 13: Captura de tela do *script solvedss.py***

**Fonte:** O Autor (2024).

> [!IMPORTANT] 
> O arquivo *requirements.txt* lista todas as bibliotecas e as suas respectivas versões necessárias para a utilização dos *scripts* listados e disponíveis no diretório.

## [](#header-2)3 - Como citar esta biblioteca

Utilizando essa biblioteca, cite os seguintes trabalhos: 

>SOUZA, Arthur Gomes de; JUNIOR, Julio; GUEDES, Michele; BERNARDES, Wellington Maycon S. Coordinating distribution power system protection in a utility from Uberlândia - MG using a geographic database, QGIS and OpenDSS. *In*: THE XIV LATIN-AMERICAN CONGRESS ON ELECTRICITY GENERATION AND TRANSMISSION - CLAGTEE 2022, 14., 2022, Rio de Janeiro, Brazil. Anais... Rio de Janeiro, 2022. p. 1-9. 

>SOUZA, Arthur Gomes de; BERNARDES, Wellington Maycon S.; PASSATUTO, Luciana A. T. Aquisição de dados topológicos e coordenação de religadores usando as ferramentas de apoio QGIS e OpenDSS. *In*: IEEE INTERNATIONAL CONFERENCE ON INDUSTRY APPLICATIONS (INDUSCON), 15., 2023, São Bernardo do Campo, Brazil. Anais... São Bernardo do Campo: IEEE, 2023. p. 607-608. doi: 10.1109/INDUSCON58041.2023.10374830.

>PASSATUTO, Luiz Arthur. T.; SOUZA, Arthur Gomes de; BERNARDES, Wellington Maycon S.; FREITAS, Lúcio C. G.; RESENDE, Ênio C. Assignment of Responsibility for Short-Duration Voltage Variation via QGIS, OpenDSS and Python. *In*: INTERNATIONAL WORKSHOP ON ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING FOR ENERGY TRANSFORMATION (AIE), 2024, Vaasa, Finland. Anais... Vaasa: IEEE, 2024. p. 1-6. doi: 10.1109/AIE61866.2024.10561325.

## Referências
[^Ref-BDGD]
[^Ref-ManualBDGD]
[^Ref-Prodist]
[^Ref-Microsoft]
[^Ref-Python]
[^Ref-QGIS]

[^Ref-BDGD]: AGÊNCIA NACIONAL DE ENERGIA ELÉTRICA (ANEEL). Dados abertos do Banco de Dados Geográficos de Distribuição - BDGD. Disponível em: [https://dadosabertos-aneel.opendata.arcgis.com/search?tags=distribuicao](https://dadosabertos-aneel.opendata.arcgis.com/search?tags=distribuicao). Acesso em: 27 ago. 2024.

[^Ref-ManualBDGD]: AGÊNCIA NACIONAL DE ENERGIA ELÉTRICA (ANEEL). Manual de Instruções da BDGD. Disponível em: [https://www.gov.br/aneel/pt-br/centrais-de-conteudos/manuais-modelos-e-instrucoes/distribuicao](https://www.gov.br/aneel/pt-br/centrais-de-conteudos/manuais-modelos-e-instrucoes/distribuicao). Acesso em: 27 ago. 2024.

[^Ref-Prodist]: AGÊNCIA NACIONAL DE ENERGIA ELÉTRICA (ANEEL). Procedimentos de Distribuição de Energia Elétrica no Sistema Elétrico Nacional – PRODIST: Módulo 10. Disponível em: [https://www.gov.br/aneel/pt-br/centrais-de-conteudos/procedimentos-regulatorios/prodist](https://www.gov.br/aneel/pt-br/centrais-de-conteudos/procedimentos-regulatorios/prodist). Acesso em: 27 ago. 2024.

[^Ref-Microsoft]: MICROSOFT. Visual Studio Code. Disponível em: [https://code.visualstudio.com/download](https://code.visualstudio.com/download). Acesso em: 27 ago. 2024.

[^Ref-Python]: PYTHON SOFTWARE FOUNDATION. Python. Disponível em: [https://www.python.org/downloads/](https://www.python.org/downloads/). Acesso em: 27 ago. 2024.

[^Ref-QGIS]: QGIS. QGIS Geographic Information System. Disponível em: [https://qgis.org/download/](https://qgis.org/download/). Acesso em: 27 ago. 2024.

