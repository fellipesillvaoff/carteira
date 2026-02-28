# 📈 Asset Management System (Sistema de Gestão de Fundo e Cotas)

[🇬🇧 English](#english) | [🇵🇹/🇧🇷 Português](#português) | [🇪🇸 Español](#español) | [🇨🇳 中文](#chinese)

---

> ⚠️ **IMPORTANT WARNING / AVISO IMPORTANTE / ADVERTENCIA IMPORTANTE / 重要警告** > 
> **(EN)** This software is currently in the **Testing Phase (Beta)**. It may contain bugs, calculation errors, or unexpected behaviors. Do not use it for critical financial decisions without manually verifying the data. Use at your own risk.
> 
> **(PT)** Este software encontra-se em **Fase de Testes (Beta)**. Pode conter falhas, erros de cálculo ou comportamentos inesperados. Não o utilize para tomar decisões financeiras críticas sem verificar os dados manualmente. O uso é da sua inteira responsabilidade.
> 
> **(ES)** Este software se encuentra en **Fase de Pruebas (Beta)**. Puede contener errores de cálculo o comportamientos inesperados. No lo utilice para decisiones financieras críticas sin verificar los datos manualmente. Úselo bajo su propio riesgo.
> 
> **(ZH)** 本软件目前处于**测试阶段 (Beta)**。它可能包含错误、计算偏差或意外行为。在未手动核实数据的情况下，请勿将其用于关键的财务决策。使用风险自负。

---

## <a id="english"></a> 🇬🇧 English

### Overview
A Python-based desktop application designed to manage personal investment portfolios or small private funds. It tracks investments, calculates quota values for multiple investors, and provides advanced institutional-grade metrics.

### Key Features
* **Quota Management**: Control deposits and withdrawals for multiple investors using an investment fund quota system.
* **Mark-to-Market (MTM)**: Update asset prices and automatically save historical portfolio snapshots.
* **Advanced Metrics**: 
    * Calculates **Exact XIRR (TIR)** based on the real lifespan of each asset using `scipy.optimize`.
    * Calculates the **Sharpe Ratio** by fetching the Brazilian CDI benchmark directly from the Central Bank of Brazil via API (`python-bcb`).
* **Complete Tracking**: Register trades, dividends, amortizations, and administrative expenses.
* **Local Database**: 100% offline and secure using SQLite.

### Installation
1. Clone this repository.
2. Install the required libraries:
   ```bash
   pip install customtkinter pandas sqlite3 numpy numpy-financial scipy python-bcb matplotlib Pillow
