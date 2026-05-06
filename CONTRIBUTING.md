# Contribuindo para o PyOPL-Utility 🚀

Primeiramente, obrigado por se interessar em contribuir! Este projeto foi criado por um estudante de Engenharia de Software e entusiasta de retrogaming, e toda ajuda é bem-vinda para tornar a gestão de jogos de PS2 no Linux mais fácil.

Como este é um projeto focado em **Engenharia de Software**, buscamos manter um código limpo, modular e bem documentado.

## 📋 Como posso contribuir?

### 1. Relatando Bugs 🐛
Se você encontrar um erro, abra uma **Issue** descrevendo:
- O que aconteceu.
- O que era esperado que acontecesse.
- O seu sistema operacional e versão do Python.
- Passos para reproduzir o erro.

### 2. Sugerindo Melhorias ✨
Tem uma ideia de funcionalidade nova? Abra uma **Issue** com a tag `enhancement` e descreva como essa funcionalidade ajudaria os usuários.

### 3. Enviando Código (Pull Requests) 💻
Se você quer colocar a mão na massa:
1. Faça um **Fork** do projeto.
2. Crie uma branch para sua modificação:
   - Para bugs: `git checkout -b fix/nome-do-bug`
   - Para novas funcionalidades: `git checkout -b feature/nome-da-feature`
3. Faça suas alterações seguindo os padrões de código (veja abaixo).
4. **Teste seu código!** Garanta que a lógica principal não foi quebrada.
5. Envie um **Pull Request** descrevendo detalhadamente o que você mudou.

## 🛠️ Padrões de Código

Para manter o projeto organizado, seguimos estas diretrizes:

*   **Python (PEP 8):** Tente seguir as convenções de estilo do Python.
*   **Modularização:** 
    *   Lógica de arquivos e binários -> pasta `core/`.
    *   Interface visual -> pasta `ui/`.
    *   Scripts de entrada -> raiz (`app.py`, `cli.py`).
*   **Comentários:** Comente partes complexas do código, especialmente na manipulação de arquivos binários (`ul.cfg`).

## 🧪 Testes

Antes de enviar um código que altere a forma como as ISOs são lidas ou divididas, certifique-se de testar com ISOs reais ou mocks controlados. Se o seu código adicionar uma nova funcionalidade, considere adicionar documentação de como testá-la.

## 💬 Comunicação

Se tiver dúvidas técnicas sobre a estrutura do projeto ou sobre o algoritmo de split das ISOs, sinta-se à vontade para perguntar diretamente nas Discussions ou abrir uma Issue de dúvida.

Trabalhar juntos é a melhor forma de aprender Engenharia de Software! 🎮
