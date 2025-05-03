# Dashboard de Pré-Inscrições — Escola Profissional da Ilha de São Jorge

Esta aplicação permite visualizar e analisar dados de pré-inscrições de alunos através de uma interface interativa feita com [Streamlit](https://streamlit.io/). Os dados podem ser carregados via ficheiro (`CSV`, `Excel`, `TXT/JSON`) ou diretamente de uma base de dados MySQL remota.

## 🔧 Funcionalidades

- Login para acesso administrativo
- Carregamento de dados por ficheiro ou base de dados
- Cálculo automático de idade e ano letivo
- Filtros por ano letivo, curso e escola de origem
- Gráficos interativos com Plotly:
  - Distribuição por ilha
  - Distribuição etária (total e 14–25 anos)
  - Distribuição por género
  - Cursos escolhidos (1ª, 2ª e 3ª opções)
  - Mapa com inscrições por ilha
- Exportação de dados filtrados e gráficos

## 📦 Requisitos

O ficheiro `requirements.txt` inclui:

```
streamlit
pandas
plotly
openpyxl
sqlalchemy
pymysql
requests
xlsxwriter
```

## 🚀 Como executar

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar a aplicação
streamlit run dashboard.py
```

## 🌐 Publicar na Streamlit Cloud

1. Cria um repositório GitHub com:
   - `dashboard.py`
   - `requirements.txt`
   - `README.md`

2. Vai a [https://streamlit.io/cloud](https://streamlit.io/cloud) e faz login.

3. Faz deploy da app diretamente a partir do GitHub.

## 🔒 Ligação à Base de Dados

Para importar dados automaticamente de um formulário online:

1. Cria um utilizador MySQL e dá acesso remoto no cPanel.
2. Adiciona no código:
   ```python
   db_user = "teu_utilizador"
   db_pass = "tua_senha"
   db_host = "host_mysql"
   db_port = "3306"
   db_name = "nome_da_base"
   table_name = "inscricoes"
   ```

> **Nota:** Usa um utilizador com permissões limitadas (só leitura).

## 🧑‍🏫 Desenvolvido por

Joel Cunha — Escola Básica e Secundária da Calheta  
Mais info: [episj.com](https://www.episj.com)
# episjdashbaord
