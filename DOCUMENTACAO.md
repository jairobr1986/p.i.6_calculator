# Documentação técnica — Simula+

> Versão documentada em 03 de setembro de 2026.

## 1. Visão geral

O **Simula+** é uma aplicação web estática para comparar a viabilidade financeira entre aquisição financiada e locação de veículos. Ela foi projetada para ser simples de usar em celular, sem instalação, servidor, banco de dados ou dependências externas.

Os cálculos ocorrem exclusivamente no navegador do visitante. A aplicação não concede crédito, não consulta bancos ou sistemas de parceiros e não substitui uma proposta comercial.

## 2. Funcionalidades

| Área | O que faz |
|---|---|
| Comparação de alternativas | Calcula o custo total estimado de compra financiada e locação no mesmo período e destaca a alternativa de menor custo. |
| Financiamento | Considera preço, entrada, prazo e taxa mensal informados pelo usuário. |
| Custos de propriedade | Inclui seguro, IPVA proporcional e manutenção mensal, quando informados. |
| Locação | Aceita tarifa mensal ou diária informada pela empresa/parceiro. |
| Histórico | Mantém as últimas cinco simulações somente no navegador do usuário; pode ser apagado a qualquer momento. |
| Temas | Inclui os temas Padrão, Claro e Escuro; a preferência é preservada no navegador. |
| Responsividade | Interface mobile-first, adaptada para celular, tablet e desktop. |
| PWA | Pode ser instalada como app no Android após a publicação em HTTPS e mantém os arquivos principais em cache para uso offline. |

## 3. Tecnologias

- HTML5
- CSS3, incluindo Media Queries e variáveis CSS
- JavaScript puro (ECMAScript)
- `localStorage` do navegador para tema e histórico

Não há framework, pacote NPM, processo de build ou variável de ambiente.

## 4. Estrutura de arquivos

```text
Calculadora nova/
├── css/
│   ├── index.html                         # Estrutura e textos da interface
│   ├── style.css                          # Design responsivo e temas
│   ├── script.js                          # Regras de cálculo e interações
│   ├── manifest.webmanifest               # Metadados de instalação PWA
│   ├── sw.js                              # Cache offline do PWA
│   └── icon.svg                           # Ícone do aplicativo
│   └── Calculadora.png                    # Imagem existente no projeto
├── docs/
│   └── estrutura_completa_*.txt           # Registro da estrutura original
├── DOCUMENTACAO.md                        # Esta documentação completa
├── README.md                              # Entrada rápida do repositório
└── gerador_de_estrutura_analise_code.py   # Utilitário existente para gerar estrutura
```

> A pasta chamada `css` foi mantida por compatibilidade com a estrutura original, mas nela ficam também o HTML e o JavaScript.

## 5. Como executar localmente

Como este é um site estático, basta abrir [css/index.html](css/index.html) em um navegador moderno.

Para uma experiência de desenvolvimento mais próxima de produção, use a extensão **Live Server** do VS Code ou qualquer servidor estático. Não é necessário instalar dependências.

## 6. Como publicar na Vercel

1. Crie um repositório no GitHub e envie todos os arquivos desta pasta.
2. Na Vercel, clique em **Add New → Project** e selecione o repositório.
3. Em **Root Directory**, escolha `css`.
4. Escolha o framework **Other**.
5. Não informe comando de build nem diretório de saída.
6. Clique em **Deploy**.

Após o deploy, confirme que a URL abre diretamente a calculadora. Cada novo `push` para a branch configurada no GitHub gerará um novo deploy.

No Android, abra a URL no Chrome e selecione **Instalar app** ou **Adicionar à tela inicial** no menu. A instalação exige HTTPS, condição já atendida pela Vercel.

## 7. Uso da aplicação

### 7.1 Veículo

1. Selecione a aba **Veículo**.
2. Informe preço de compra, entrada, prazo, taxa mensal do financiamento e custos mensais de propriedade.
3. A entrada e os custos de propriedade podem ser zero, mas a entrada não pode ser maior que o preço do veículo.
4. Escolha a locação mensal ou diária e informe a tarifa recebida.
5. Clique em **Comparar compra e locação**.

### 7.2 Temas e histórico

- O botão com o símbolo de sol abre a seleção de temas.
- O botão com o relógio abre o histórico das últimas cinco simulações.
- O histórico é salvo localmente; ao limpar os dados do navegador, ele também pode ser apagado.

## 8. Regras de cálculo

### 8.1 Financiamento de veículo

O valor financiado é:

```text
valor financiado = valor do veículo − entrada
```

As parcelas usam a fórmula Price:

```text
parcela = PV × i × (1 + i)^n / ((1 + i)^n − 1)
```

Onde `PV` é o valor financiado, `i` é a taxa mensal e `n` é a quantidade de parcelas.

A taxa mensal é informada pelo usuário conforme a proposta de financiamento recebida. Dessa forma, o app não presume taxas de mercado e pode ser usado com as condições fornecidas pela PW Motors ou por outra instituição.

### 8.2 Locação de veículo

Para locação mensal, o custo é `tarifa mensal × prazo em meses`. Para locação diária, o custo é `tarifa diária × prazo em meses × 30`.

### 8.3 Comparação final

```text
total da compra = entrada + (parcela × prazo) + (custo mensal de propriedade × prazo)
diferença = |total da compra − total da locação|
```

O sistema destaca a alternativa de menor custo no período informado. Ele não calcula custos não informados, como combustível, franquia, multas, depreciação, valor de revenda ou coberturas específicas; esses pontos devem ser avaliados na proposta real.

## 9. Persistência e privacidade

| Informação | Onde fica | Como remover |
|---|---|---|
| Tema escolhido | `localStorage` (`simulap-theme`) | Escolha outro tema ou limpe os dados do site. |
| Últimas cinco simulações | `localStorage` (`simulap-history-v1`) | Use **Limpar histórico** na janela de histórico ou limpe os dados do site. |

O projeto não possui API, cookies próprios, login, banco de dados ou envio de dados pessoais. Ainda assim, não é recomendável usar informações sensíveis reais em uma versão de demonstração pública.

## 10. Manutenção

| Alteração desejada | Onde fazer |
|---|---|
| Rótulos, campos e textos de aviso | [css/index.html](css/index.html) |
| Cores, espaçamento, temas e responsividade | [css/style.css](css/style.css) |
| Fórmulas, validações e histórico | [css/script.js](css/script.js) |
| Orientações do repositório | [README.md](README.md) e este arquivo |

### Cuidados antes de alterar regras financeiras

1. Atualize a constante ou a fórmula em `script.js`.
2. Atualize esta documentação e os textos de aviso na interface.
3. Teste casos sem entrada, taxa zero, parcelas inválidas, tarifa mensal e tarifa diária.
4. Valide as condições com a empresa/parceiro antes de publicar uma nova regra.

## 11. Checklist de testes manuais

- [ ] Trocar entre os três temas e recarregar a página.
- [ ] Testar entrada igual ao valor do veículo e entrada maior que o valor.
- [ ] Testar locação mensal e diária.
- [ ] Testar juros zero e custos de propriedade vazios.
- [ ] Fazer seis simulações e confirmar que apenas cinco ficam no histórico.
- [ ] Limpar o histórico e confirmar que os cartões desaparecem.
- [ ] Conferir a interface em celular, tablet e desktop.

## 12. Limitações conhecidas e próximos passos sugeridos

- Não há integração com estoque, preços, propostas ou sistemas da PW Motors.
- Os valores de financiamento, propriedade e locação devem ser informados pelo usuário e validados comercialmente.
- O histórico é local e não sincroniza entre aparelhos.
- A aplicação pode receber, no futuro, um ícone/manifesto PWA, testes automatizados, exportação de simulação em PDF e uma área administrativa para editar taxas sem alterar código.

## 13. Créditos e apoio de IA

Esta versão foi elaborada com assistência do **Codex (OpenAI)**, em colaboração com o responsável pelo projeto.

O apoio de IA nesta versão incluiu:

- análise da estrutura original e preservação das funcionalidades de veículo e aluguel;
- reorganização da interface para uma experiência mobile-first com aparência de aplicativo;
- criação dos temas Padrão, Claro e Escuro;
- adequação de campos financeiros para teclado numérico em celulares;
- adequação do projeto ao escopo acadêmico de comparação entre compra e locação de veículos;
- inclusão de custos de propriedade e de tarifas de locação mensais ou diárias na comparação;
- implementação do histórico local das últimas cinco simulações;
- comentários no código e criação desta documentação de manutenção e deploy.

A responsabilidade pela validação das regras de negócio, condições financeiras, conteúdo publicado e conformidade legal permanece com os responsáveis pelo projeto.
