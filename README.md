# 📊 Organizador de Estudos Pessoal (v3.0 - Database Edition)

Sistema de linha de comando (CLI) desenvolvido em **Python** para gestão de produtividade acadêmica. O projeto evoluiu de um registro em texto simples para uma ferramenta robusta utilizando **Banco de Dados Relacional (SQLite)**, permitindo um controle profissional e persistente sobre os registros de estudo.

---

## 🚀 Novidades da Versão 3.0 (SQL)

* **Persistência com SQLite3:** Substituição de arquivos `.txt` por um banco de dados real (`.db`), garantindo integridade dos dados e consultas mais rápidas.
* **CRUD Completo:** Implementação de funções para **C**reate (Registrar), **R**ead (Ver Histórico), **U**pdate (Editar) e **D**elete (Excluir registro específico ou limpar banco).
* **Relatórios via SQL:** Uso de funções de agregação (`SUM` e `GROUP BY`) para gerar estatísticas automáticas de tempo por categoria (**Teoria, Prática, Revisão**).
* **Gerenciamento de IDs:** Cada registro possui um identificador único, facilitando a edição e exclusão de entradas específicas.
* **Robustez (Error Handling):** Tratamento de exceções em todas as entradas de dados, impedindo que o programa feche por erros de digitação.

---

## 🎥 Demonstração na Prática
*(Arraste seu vídeo de demonstração para esta linha para carregar no GitHub)*
[Vídeo do programa funcionando]

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.12**
* **SQLite3:** Banco de dados relacional nativo.
* **Colorama:** Estilização e UX (User Experience) no terminal.
* **OS:** Gerenciamento de arquivos e caminhos.

---

## ⚙️ Como Executar o Projeto

Para testar o organizador na sua máquina, siga os passos abaixo:

1.  **Clonar o repositório:**
    ```bash
    git clone [https://github.com/thurr-vini/organizador-estudos-python.git](https://github.com/thurr-vini/organizador-estudos-python.git)
    ```

2.  **Instalar dependências:**
    ```bash
    pip install colorama
    ```

3.  **Rodar a aplicação:**
    ```bash
    python main.py
    ```
    *Nota: O banco de dados `historico_estudos.db` será criado automaticamente na primeira execução.*

---

## 👤 Autor

**Arthur Vinícius Gomes Souza** *Estudante de Ciência da Computação (3º Período) - **UniNassau*** 📍 Arara - PB / Campina Grande - PB  

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/thurr-vini)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/arthur-vinícius-169a92307)

---

## 📄 Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.