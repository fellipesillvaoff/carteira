# 📈 Asset Management System (Gestão Institucional de Fundos e Cotas)

Um sistema desktop avançado desenvolvido em Python para a gestão de carteiras de investimentos, controle de múltiplos cotistas e marcação a mercado. 

> ⚠️ **AVISO IMPORTANTE / IMPORTANT WARNING** <br>
> Este software encontra-se em **Fase de Testes (Beta)**. Pode conter falhas, erros de cálculo ou comportamentos inesperados. Não o utilize para tomar decisões financeiras críticas ou auditorias oficiais sem verificar os dados matemáticos manualmente. O uso é de sua inteira responsabilidade.

---

## 🎯 Sobre o Projeto e Aplicabilidade (RPPS Municipal)

Este sistema foi arquitetado com lógicas de fundos de investimentos reais. Além de ser excelente para a gestão de patrimônio pessoal ou clubes de investimento privados, **ele é uma ferramenta incrivelmente útil para o controle de ativos de RPPS (Regime Próprio de Previdência Social) Municipal**. 

Com ele, gestores e comitês de investimentos de RPPS podem:
* Monitorar a evolução do patrimônio líquido do instituto em tempo real.
* Registrar o histórico exato de fechamento diário/mensal (Snapshots) para auditoria.
* Comparar a rentabilidade da carteira diretamente com o CDI (e futuramente metas atuariais como IPCA+) através da integração com o Banco Central.
* Controlar aportes (repasses previdenciários) e saques (pagamento de benefícios) sem distorcer a rentabilidade histórica dos investimentos.

---

## 🧠 Sobre o Desenvolvedor

Este projeto foi idealizado e desenvolvido por um **Analista de Investimentos com Mestrado em Economia Aplicada**. 

A arquitetura do software reflete anos de experiência prática no mercado financeiro institucional e na gestão de carteiras, combinando teorias econômicas avançadas (como Otimização de Portfólios de Markowitz e *Arbitrage Pricing Theory*) com o desenvolvimento de ferramentas de automação e análise de dados em Python. O foco principal do desenvolvimento foi trazer métricas de nível institucional (como XIRR e Sharpe dinâmico) para uma interface acessível e offline.

---

## ✨ Funcionalidades do Sistema

O sistema é dividido em módulos operacionais para garantir a segregação de dados e a precisão contábil:

### 1. 📊 Dashboard e Analytics
* **Sumário:** Visão em tempo real do Patrimônio Líquido, Caixa Livre e Valor da Cota. Gráfico interativo de evolução patrimonial.
* **Métricas Institucionais:** Cálculo automático do **Índice de Sharpe**, ROI da carteira e lucros/prejuízos nominais.
* **TIR Exata (XIRR):** Utiliza a biblioteca `scipy.optimize` para calcular a Taxa Interna de Retorno anualizada de cada ativo, ponderando as datas exatas de cada aporte, dividendo e preço atual.
* **Gráficos Dinâmicos:** Alocação por classe, por ativo e top rentabilidades.

### 2. 📸 Marcação a Mercado (Snapshots)
* **Preços de Fechamento:** Atualize os preços dos ativos em datas específicas. O sistema tira uma "foto" (Snapshot) da carteira, salvando o valor total para fins de histórico e auditoria.
* **Histórico Contínuo:** Tabela dedicada para auditar como estava a carteira no dia exato de qualquer mês passado.

### 3. 👥 Gestão de Cotistas
* Sistema de cotas real. Novos aportes ou saques de capital não distorcem a rentabilidade de quem já está no fundo.
* O sistema calcula automaticamente quantas cotas o investidor adquire com base no fechamento do dia.
* **Exportação para Excel (.xlsx):** Gere relatórios de cotistas com apenas um clique.

### 4. 💸 Mesa de Operações e Proventos
* **Trading:** Registro de compras e vendas de ativos (Ações, FIIs, Renda Fixa, BDRs, etc.) com cálculo automático de preço médio e dedução de caixa/custos.
* **Proventos & Despesas:** Lançamento de Dividendos, JCP, Amortizações e Taxas Administrativas que afetam o caixa livre do fundo.

### 5. 📉 Benchmark Integrado (Banco Central)
* Esqueça a digitação manual de índices. O sistema se conecta via API (`python-bcb`) ao Banco Central do Brasil (SGS 12) para baixar a curva real do CDI diário.
* Gera um gráfico interativo comparando a Rentabilidade Acumulada da sua Cota contra o CDI no mesmo período de tempo (a partir da data de criação do fundo).

### 6. 🗄️ Editor de Banco de Dados Embutido
* Ferramenta de administrador para editar valores diretamente no SQLite, excluir lançamentos errados e **Recalcular Saldos**. O sistema varre todo o histórico e reconstrói a posição financeira atual para corrigir bugs humanos.
* Suporte a múltiplas carteiras (arquivos `.db` externos).

---

## 🚀 Instalação e Requisitos

O sistema requer Python 3.8+ e as seguintes bibliotecas para funcionar corretamente:

```bash
# Clone o repositório
git clone [https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git](https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git)
cd SEU_REPOSITORIO

# Instale as dependências matemáticas, de dados e de interface
pip install customtkinter pandas sqlite3 numpy numpy-financial scipy python-bcb matplotlib mplcursors Pillow openpyxl
