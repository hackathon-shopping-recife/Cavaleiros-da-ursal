# Cavaleiros-da-ursal
O protótipo deste projeto é formado por um arquivo com os endpoints de comunicação (index.py) desenvolvido em Flask (Python) que usa o arquivo index.html na pasta templates, onde está todo o código em css, html e js. O que, por ventura, estiver ai de extra após a deadline p subir o código, é pq não deu tempo de apagar.

O index.py serve de ponte entre o usurio e o chatbot. Através dele, as mensagens so enviadas e recebidas e as requisições so processadas. O serviço de chatbot utilizado foi o Google Dialogflow.

Fora esses arquivos, temos alguns ipython notebooks com rotinas de construção de bases de dados:
- Simulamos o gosto de alguns perfis de usuários p testar o algoritmo de recomendação;
- Juntamos os dados das lojas em um csv (fornecidos pelo shopping);
- Usamos um crawler p pegar informações das redes sociais das lojas para saber quando houve e não houve promoção para sinalizar ao usuário.
Estes scripts podem ser facilmente colocados em um arquivo só e executados através de algum serviço de gerenciamento de DAGs, como o Luigi, por exemplo.

Resumindo, o que fizemos:
- Mecanismo de treinamento do algoritmo de recomendação SVD (Filtro Colaborativo), tecnologia semelhante à utilizada no Netflix, Spotify... Os modelos são salvos em arquivos de formato especficos da lib usada (surprise).
- Boas-vindas da Clarice;
- Fluxo de pedido de dicas de ofertas/promoções com preferência de item, com preferÊncia de loja e sem nenhuma preferência.
- Implementamos o mecanismo de recomendação para recomendação geral, sem preferências específicas que afunilaria a resposta.
- Capturamos se o usuário gostou ou não de um conjunto de recomendaçes, o que alimenta o algoritmo de recomendação.

O que QUASE fizemos:
- Leitura de QR-Code. Achei um código totalmente funcional mas por um choque da necessidade do dialogflow conversar c um serviço HTTP e a câmera s abrir para serviços HTTPS, não deu tempo de fazer as gambiarras necessárias. O da tentativa é o index_http.py. A ideia era criar um serviço HTTP intermediário e servir de bypass para o HTTPS que ficaria toda a inteligência.
