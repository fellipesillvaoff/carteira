# 📈 Asset Management System (Gestão Institucional de Fundos e Cotas)

Um sistema desktop avançado desenvolvido em Python para a gestão de carteiras de investimentos, controle de múltiplos cotistas, marcação a mercado e auditoria de compliance. 

> ⚠️ **AVISO IMPORTANTE / IMPORTANT WARNING** <br>
> Este software encontra-se em **Fase de Testes (Beta)**. Pode conter falhas, erros de cálculo ou comportamentos inesperados. Não o utilize para tomar decisões financeiras críticas ou auditorias oficiais sem verificar os dados matemáticos manualmente. O uso é de sua inteira responsabilidade.
> A versão 3.4.0, não é compativél com as versão anteriores, devido a mudança nas tabelas e na estrutura de salvamento de históricos de cotas dos ativos.

---

## 🎯 Sobre o Projeto e Aplicabilidade (RPPS Municipal tanto para 4963/2021 quanto para 5272/2025)

Este sistema foi arquitetado com lógicas de fundos de investimentos reais. Além de ser excelente para a gestão de patrimônio pessoal ou clubes de investimento privados, **ele é uma ferramenta incrivelmente útil para o controle de ativos de RPPS (Regime Próprio de Previdência Social) Municipal**. 

Com ele, gestores e comitês de investimentos de RPPS podem:
* Monitorar a evolução do patrimônio líquido do instituto em tempo real.
* Registrar o histórico exato de fechamento diário/mensal (Snapshots) para auditoria.
* Garantir o estrito cumprimento das diretrizes de alocação (como a **Resolução CMN 5272**) através do painel de Enquadramentos.
* Comparar a rentabilidade da carteira diretamente com o CDI (e futuramente metas atuariais como IPCA+) através da integração com o Banco Central.
* Controlar aportes (repasses previdenciários) e saques (pagamento de benefícios) sem distorcer a rentabilidade histórica dos investimentos via sistema de cotas.

---

## 🧠 Sobre o Desenvolvedor

Este projeto foi idealizado e desenvolvido por um **Analista de Investimentos com Mestrado em Economia Aplicada**. 

A arquitetura do software reflete anos de experiência prática no mercado financeiro institucional e na gestão de carteiras, combinando teorias econômicas avançadas (como Otimização de Portfólios de Markowitz e *Arbitrage Pricing Theory*) com o desenvolvimento de ferramentas de automação e análise de dados em Python. O foco principal do desenvolvimento foi trazer métricas de nível institucional (como XIRR, DRE de período fechado e Sharpe dinâmico) para uma interface acessível e offline.

---

## ✨ Funcionalidades do Sistema

O sistema é dividido em módulos operacionais para garantir a segregação de dados, a precisão contábil e a facilidade de auditoria:

### 1. 📊 Dashboard e Analytics
* **Sumário:** Visão em tempo real do Patrimônio Líquido, Caixa Livre e Valor da Cota. Gráfico interativo de evolução patrimonial.
* **Métricas Institucionais:** Cálculo automático do **Índice de Sharpe**, ROI da carteira e lucros/prejuízos nominais em aberto.
* **TIR Exata (XIRR):** Utiliza a biblioteca `scipy.optimize` para calcular a Taxa Interna de Retorno anualizada de cada ativo, ponderando as datas exatas de cada aporte, dividendo e preço de marcação a mercado.
* **Gráficos Dinâmicos:** Alocação por classe, por ativo e top rentabilidades.

### 2. ⚖️ Enquadramentos e Compliance (Políticas de Investimento)
* Módulo dedicado à gestão de risco e adequação regulatória.
* **Criação de Regras:** Defina limites percentuais máximos de alocação (ex: "Art. 7 - Renda Fixa: Máx 80%").
* **Monitoramento Visual:** Vincule ativos às regras criadas e acompanhe o nível de exposição através de KPIs visuais que ficam vermelhos caso o limite da política de investimentos seja ultrapassado.

### 3. 📉 Apuração de Rendimento (DRE por Período Fechado)
* Calcule a performance financeira exata do fundo entre duas datas quaisquer.
* O algoritmo consolida automaticamente múltiplos eventos de caixa utilizando a fórmula contábil institucional: `Saldo Final + Resgates (Vendas/Proventos) - Aplicações (Compras) - Saldo Inicial`.
* **Geração de Relatórios:** Exportação direta dos resultados para Excel (`.xlsx`), ideal para prestação de contas.

### 4. 📸 Marcação a Mercado e Histórico de Ativos
* **Snapshots:** Atualize os preços dos ativos em datas específicas. O sistema tira uma "foto" da carteira e salva o valor da cota no banco de dados para desenhar gráficos precisos.
* **Filtros de Auditoria:** Tabela de histórico avançada com motor de busca por Data e Ticker para rastrear a posição exata da carteira no passado.

### 5. 👥 Gestão de Cotistas
* Sistema de cotas institucional. Novos aportes ou saques de capital não diluem ou distorcem a rentabilidade de quem já está no fundo.
* O sistema calcula matematicamente as frações de cotas adquiridas com base no valor de fechamento (Snapshot) mais recente.

### 6. 💸 Mesa de Operações e Fluxo de Caixa
* **Trading Seguro:** Registro de compras e vendas com visualização do **Caixa Livre em tempo real**. O sistema bloqueia ordens que não possuam saldo suficiente.
* **Lupa de Busca:** Pesquise ativos rapidamente para descobrir seu Preço Médio e quantidade atual antes de operar.
* **Proventos & Despesas:** Lançamento de Dividendos, JCP, Amortizações e Taxas que injetam ou deduzem capital diretamente do Caixa Livre.

### 7. 📈 Benchmark Integrado (Banco Central)
* Esqueça a digitação manual de índices. O sistema se conecta via API (`python-bcb`) ao Banco Central do Brasil (SGS 12) para baixar a curva real do CDI.
* Gráfico interativo comparando a evolução da sua Cota contra o CDI Acumulado no mesmo período.

### 8. 🗄️ Editor de Banco de Dados Embutido
* Ferramenta *sysadmin* para editar valores diretamente no SQLite ou excluir lançamentos incorretos.
* **Botão "Recalcular Saldos":** Varre todo o histórico de *trades* e movimentações (do dia zero até hoje) e reconstrói a posição financeira atual, Preço Médio e Caixa para corrigir falhas humanas.
* Suporte nativo à alternância entre múltiplas carteiras (arquivos `.db`).

---

## 🚀 Instalação e Requisitos

O sistema requer Python 3.8+ e as seguintes bibliotecas para funcionar corretamente:

```bash
# Clone o repositório
git clone [https://github.com/fellipesillvaoff/carteira.git](https://github.com/fellipesillvaoff/carteira.git)
cd carteira

# Crie e ative um ambiente virtual (Opcional, mas recomendado)
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Instale as dependências
pip install customtkinter pandas sqlite3 numpy numpy-financial scipy python-bcb matplotlib mplcursors Pillow openpyxl

# Execute o sistema
python main.py


###Tela cotista
<img width="1225" height="798" alt="image" src="https://github.com/user-attachments/assets/a904bfb6-ec8e-454d-bf7a-a0b9bf9706c9" />


###Tela Enquadramento
<img width="1194" height="772" alt="image" src="https://github.com/user-attachments/assets/f15ec2ee-730a-4d9c-b81e-64c208c9ae0d" />

