# PyOPL-Utility 🎮🐧

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**PyOPL-Utility** é uma ferramenta nativa para Linux desenvolvida para gerenciar bibliotecas de jogos de PlayStation 2 para o **Open PS2 Loader (OPL)**. Este projeto elimina a necessidade de usar ferramentas legadas de Windows via Wine, oferecendo uma solução robusta para manipulação de ISOs.

## 📂 Estrutura do Projeto

A arquitetura foi desenhada seguindo princípios de modularidade:

*   **`app.py`**: Ponto de entrada da interface gráfica (GUI).
*   **`cli.py`**: Interface de linha de comando para automação e uso via terminal.
*   **`core/`**: O "motor" do sistema.
    *   `iso_handler.py`: Manipulação e leitura de metadados de arquivos ISO.
    *   `renamer.py`: Lógica de padronização de nomes (GameID.Nome.iso).
    *   `splitter.py`: Algoritmo de fragmentação de ISOs para sistemas FAT32.
*   **`ui/`**: Componentes da interface visual em PyQt.
*   **`test_data/`**: Amostras de ISOs para validação do software.
*   **`dist/` & `build/`**: Binários gerados para distribuição.

## ✨ Funcionalidades Atuais

- [x] **Suporte Dual:** Use via Interface Gráfica (`app.py`) ou Terminal (`cli.py`).
- [x] **Extração de Metadados:** Leitura direta do Game ID (ex: SCUS-97481).
- [x] **Preparado para Build:** Configuração pronta para gerar executáveis nativos via PyInstaller (`.spec`).
- [x] **Ambiente de Testes:** Scripts inclusos para gerar ISOs falsas e testar a lógica sem precisar de arquivos gigantes.

## 🚀 Como Executar

### Pré-requisitos
Certifique-se de ter o Python 3.10+ instalado.

### Instalação
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/PyOPL-Utility.git
cd PyOPL-Utility

# Ative o ambiente virtual
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### Execução
Para abrir a interface gráfica:
```bash
python3 app.py
```

Para usar via terminal:
```bash
python3 cli.py --help
```

## 🛠️ Desenvolvimento e Testes

Para garantir a confiabilidade, o projeto conta com um gerador de ISOs de teste:
```bash
python3 test_fake_iso.py
```

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

### 👨‍💻 Nota do Desenvolvedor
Este projeto faz parte do meu estudo em **Engenharia de Software**, focando em manipulação de sistemas de arquivos, design de interfaces e arquitetura de software modular.