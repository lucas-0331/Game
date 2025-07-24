https://drive.google.com/drive/folders/1lKxs8k1TTLOJJpARZnyboVH-21O0fKZm?usp=sharing

# Labirintity

Um motor de Raycasting clássico, construído do zero em Python com a biblioteca Pygame. Inspirado nos icônicos jogos FPS dos anos 90 como Wolfenstein 3D, este projeto explora as técnicas de pseudo-3D para criar ambientes de labirinto navegáveis, com foco em otimização e arquitetura de software modular.

Este projeto foi desenvolvido como trabalho prático para a disciplina de Tópicos Especiais em Computação.

<!-- ## Captura de Tela -->
<!---->
<!-- ![Gameplay do Labirintity](gameplay.gif) -->

## Funcionalidades

O projeto foi evoluindo e hoje conta com uma arquitetura robusta e diversas funcionalidades avançadas:

- **Motor de Raycasting:** Renderização de paredes texturizadas com cálculo de perspectiva e profundidade.
- **Arquitetura Modular:** O código é organizado em controladores (`Game`), gerenciadores de renderização (`Renderer`) e de interface (`UIManager`), facilitando a manutenção e expansão.
- **Renderização Otimizada:**
  - Uso de NumPy para cálculos vetorizados.
  - Cache de colunas de textura para evitar reprocessamento.
  - Sistema de _Clipping_ vertical para renderizar paredes muito próximas sem perda de performance ou distorção visual.
- **Opções Gráficas Avançadas:**
  - Presets de qualidade (Baixo, Médio, Alto) que ajustam o número de raios e a distância da neblina.
  - Algoritmos de redimensionamento de textura que mudam com a qualidade gráfica (`scale` vs `smoothscale`).
- **Menus Interativos:**
  - Menu principal, de opções e de pausa.
  - Sistema de navegação por "pilha de estados", permitindo voltar aos menus anteriores de forma inteligente (inclusive com a tecla `ESC`).
  - Opções de mudança de resolução e modo tela cheia.
- **Sistema de Jogo:**
  - Progressão de múltiplos níveis.
  - Tela de carregamento animada (GIF) entre os níveis.
  - Sistema de interação com objetos do cenário (tecla 'E').
  - Tela de créditos com rolagem ao finalizar o jogo.

## Contexto do Projeto

Este software foi desenvolvido como requisito parcial para a disciplina de **Tópicos Especiais**, ministrada pelo professor **Ricardo Martins**, no 7º período do curso de **Ciência da Computação** do Instituto Federal do Sul de Minas Gerais (IFSULDEMINAS) - Campus Muzambinho, em 2025.

## Como Executar

### Pré-requisitos

- Python 3.8 ou superior

### Instalação

1.  Clone este repositório ou baixe os arquivos do projeto.

2.  (Recomendado) Crie e ative um ambiente virtual:

    ```bash
    python -m venv venv
    # No Windows
    .\venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```

3.  Instale as dependências necessárias a partir do arquivo `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

4.  Execute o jogo:
    ```bash
    python main.py
    ```

## Como Jogar

| Tecla | Ação                      |
| :---- | :------------------------ |
| `W`   | Mover para frente         |
| `S`   | Mover para trás           |
| `A`   | Girar para a esquerda     |
| `D`   | Girar para a direita      |
| `E`   | Interagir com o objetivo  |
| `ESC` | Pausar / Voltar nos menus |

## Créditos e Agradecimentos

- **Desenvolvimento:** Lucas Costa
- **Professor:** Ricardo Martins
- **Inspirações e Agradecimentos:**
  - id Software (pioneiros do gênero)
  - Fumito Ueda, Shinji Mikami, Hideo Kojima, John Romero (inspirações no design de jogos)
  - Comunidade Pygame
  - Lode Vandevenne (pelo seu excelente tutorial de Raycasting)
  - Google Gemini (pelo auxílio no desenvolvimento e depuração)
