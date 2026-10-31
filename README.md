# sqa-demo-complexity-router

> **Aviso:** este repositório é um projeto didático criado para demonstrar o SQA (Software Quality Assessment). Ele contém falhas de qualidade e segurança intencionais. Não use em produção. Parte do código foi gerado com apoio de IA. O contribuidor `demo-agent` é um agente de IA com identidade declarada.

CLI que responde perguntas sobre qualidade de software e escolhe o caminho conforme a complexidade da pergunta. O grafo (LangGraph) classifica a pergunta (atalho heurístico e, se preciso, um modelo pequeno), responde pela rota simples, intermediária ou complexa (com plano prévio), valida com um juiz LLM de outro modelo e, se a nota for baixa, sobe um nível e tenta de novo (no máximo 2 tentativas).

## Requisitos

* Python 3.11 a 3.13
* Uma chave da OpenAI (ou o backend falso, que roda sem rede)

## Instalação

```bash
python -m venv .venv
.venv/Scripts/activate          # Windows (no Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
pip install -e .
cp .env.example .env            # preencha a chave, os modelos e a senha do cache
```

## Variáveis de ambiente

| Variável | Uso |
|---|---|
| `OPENAI_API_KEY` | chave da OpenAI |
| `MODEL_SMALL` | classificador e rota simples |
| `MODEL_MEDIUM` | rota intermediária |
| `MODEL_STRONG` | plano e rota complexa |
| `MODEL_JUDGE` | juiz (modelo diferente do que gerou a resposta) |
| `CACHE_ADMIN_PASSWORD` | senha exigida por `--clear-cache`; vazia, a limpeza é recusada |
| `LLM_BACKEND` | `openai` (padrão) ou `fake` (offline, determinístico) |

Confira os nomes de modelo na documentação vigente da OpenAI antes de usar.

## Uso

```bash
python -m router_demo.cli --question "O que é complexidade ciclomática?"
python -m router_demo.cli --batch examples/questions.json
python -m router_demo.cli --question "..." --report relatorio.html
python -m router_demo.cli --question "..." --no-cache
python -m router_demo.cli --clear-cache --password <valor>
```

O painel mostra rota inicial e final, caminho no grafo, modelos usados, tentativas, tokens, custo estimado, nota do juiz, veredito (APROVADA ou NÃO VALIDADA), problemas apontados e a resposta. As respostas ficam em cache em `.cache/answers.json`.

**Custos:** os preços por 1k tokens são estimativas fixas no código (`TierConfig`), não valores cobrados pela OpenAI. Use-os só como ordem de grandeza.

## Estrutura

```
src/router_demo/
  config.py        configurações, constantes e TierConfig
  state.py         estado do grafo e trace
  graph.py         montagem do grafo e escalonamento
  cli.py           linha de comando
  llm/             fábrica de modelos, backend falso, cache
  routing/         tabela de regras e classificador
  answering/       tiers e fábrica de nós de resposta
  validation/      juiz e decisão pós-validação
  presentation/    painel no terminal e relatório HTML
```
