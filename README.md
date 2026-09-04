# Simula+

Calculadora web mobile-first para apoiar a decisão financeira entre compra financiada e locação de veículos.

> Projeto estático, rápido e sem dependências: os cálculos são realizados diretamente no navegador.

## Principais recursos

- Comparação direta do custo total estimado de compra e locação no mesmo período.
- Simulação de financiamento com preço, entrada, juros mensais e prazo informados.
- Inclusão de custos mensais de propriedade, como seguro, IPVA proporcional e manutenção.
- Locação mensal ou diária, com tarifas informadas pela empresa/parceiro.
- Temas Padrão, Claro e Escuro.
- Histórico local das últimas cinco simulações.
- Interface responsiva para celular, tablet e computador.
- Teclado numérico em campos financeiros para melhor uso no celular.
- PWA instalável: após publicar em HTTPS, o app pode ser instalado no Android e reutilizado offline.

## Demonstração local

Abra [index.html](index.html) em um navegador moderno. Não é necessário instalar pacotes ou executar comandos.

Para testar a instalação PWA, publique o projeto em HTTPS (por exemplo, na Vercel) e, no Chrome para Android, use o menu do navegador e escolha **Instalar app** ou **Adicionar à tela inicial**.

## Estrutura

```text
.
├── index.html           # Interface da calculadora
├── style.css            # Estilos responsivos e temas
├── script.js            # Cálculos, validações e histórico
├── manifest.webmanifest # Metadados de instalação PWA
├── sw.js                # Cache offline do PWA
├── icon.svg             # Ícone do aplicativo
├── DOCUMENTACAO.md      # Documentação técnica completa
└── gerador_de_estrutura_analise_code.py
```

## Publicação na Vercel

1. Envie este projeto para um repositório no GitHub.
2. Na Vercel, importe o repositório em **Add New → Project**.
3. Mantenha o **Root Directory** vazio (diretório padrão do repositório).
4. Selecione o framework **Other** e clique em **Deploy**.

## Aviso sobre os resultados

O simulador é educativo e não representa proposta comercial, aprovação de crédito ou orçamento definitivo. Informe as condições reais de financiamento e locação recebidas da empresa; confirme também cobertura, franquia, taxas, manutenção e demais cláusulas antes de decidir.

## Documentação completa

Consulte [DOCUMENTACAO.md](DOCUMENTACAO.md) para entender as fórmulas, a manutenção, a privacidade, os testes manuais, as limitações e os créditos desta versão.

## Créditos

Esta versão foi desenvolvida em colaboração com o responsável pelo projeto, com assistência do **Codex (OpenAI)** na evolução da interface, nos cálculos, na documentação e nas melhorias de usabilidade.
