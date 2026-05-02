---
name: optimize-data-models-power-bi
description: Comprehensive guide for optimizing Power BI Import data models to reduce size and improve performance. Use this skill whenever the user mentions Power BI performance issues, slow reports, large semantic models, slow dataset refresh, model size limits, VertiPaq optimization, or asks how to make their Power BI model faster or smaller. Also trigger for questions about Power Query optimization, DAX calculated columns vs computed columns, column data types, Auto date/time, DirectQuery vs Import mode, Composite models, or fact table grain. Activate even when the user just says "my Power BI is slow" or "my .pbix is too big" without providing further context.
---

# Power BI Data Model Optimization

You are helping the user reduce the size of a Power BI Import model and improve its performance. Work through the diagnostic questions first (unless the user has already provided enough context), then give prioritized, actionable recommendations with concrete Power Query (M) and DAX code where helpful.

## Diagnostic Phase

If the user hasn't provided enough context, ask about:
- **Model size**: How large is the .pbix file? How many rows in the main fact table(s)?
- **Pain point**: Slow reports? Slow refresh? Hitting the capacity size limit?
- **Data sources**: SQL Server, Excel, SharePoint, API?
- **History depth**: How many years/months of data are loaded?
- **Date columns**: Are there date or datetime columns in the model?
- **ID/code columns**: Are there text columns that represent numeric IDs or codes (like order numbers)?
- **Staging queries**: Are there Power Query queries that exist only to support other queries — not as final tables?

If the user provides enough upfront, skip the questions and go straight to recommendations.

---

## Technique 1 — Remove Unnecessary Columns (Vertical Filtering)

**Impact: High | Effort: Low**

Every column consumes memory. Only keep columns that serve:
- **Reporting**: filtering, grouping, summarizing, or displaying data in visuals
- **Model structure**: relationships, DAX calculations, RLS security roles, or conditional formatting

Audit each table and ask: *"Is this column referenced in any report page, relationship, or DAX measure?"* If not, remove it.

In Power Query, keep only required columns:

```m
= Table.SelectColumns(Source, {
    "OrderID", "CustomerID", "ProductID",
    "OrderDate", "Quantity", "Revenue"
})
```

> It's easier to add columns back later than to remove them after reports are built. Start with the minimum.

---

## Technique 2 — Filter Rows by Time and Entity (Horizontal Filtering)

**Impact: Very High | Effort: Low–Medium**

### Filter by Time
Limit history in fact tables using a parameter-driven cutoff date. This avoids loading decades of data when only the last 3–5 years are ever used.

1. Create a Power Query parameter: `HistoryYears` (type: Number, default: 3)
2. Apply the filter in the fact table query:

```m
let
    CutoffDate   = Date.AddYears(Date.From(DateTime.LocalNow()), -HistoryYears),
    Source       = Sql.Database("server", "db"),
    FactSales    = Source{[Schema="dbo", Item="FactSales"]}[Data],
    Filtered     = Table.SelectRows(FactSales, each [OrderDate] >= CutoffDate)
in
    Filtered
```

Changing the parameter later won't break existing reports — it only changes how much history is visible.

### Filter by Entity
Load only a subset of data (one region, business unit, or department):

```m
let
    Source    = Sql.Database("server", "db"),
    FactSales = Source{[Schema="dbo", Item="FactSales"]}[Data],
    Filtered  = Table.SelectRows(FactSales, each [Region] = "Brazil")
in
    Filtered
```

Use Power BI Template (.pbit) files with parameters to manage multiple entity-scoped models from one source.

---

## Technique 3 — Group and Summarize Fact Tables

**Impact: Up to 99% size reduction | Effort: Medium**

Pre-aggregating fact tables is the single most powerful technique. It raises the data grain and dramatically cuts row count.

**Tradeoff**: row-level detail is lost. Mitigate with a Composite model (see Technique 8) where summarized data lives in Import mode and the full-grain table stays in DirectQuery.

Example — reduce an order-line fact table to day/customer/product grain:

```m
let
    Source    = Sql.Database("server", "db"),
    FactSales = Source{[Schema="dbo", Item="FactSales"]}[Data],
    Grouped   = Table.Group(
        FactSales,
        {"OrderDate", "CustomerID", "ProductID"},
        {
            {"TotalRevenue",  each List.Sum([Revenue]),       type number},
            {"TotalQuantity", each List.Sum([Quantity]),      type number},
            {"OrderCount",    each Table.RowCount(_),         type number}
        }
    )
in
    Grouped
```

For even more reduction, group by **month** instead of day:

```m
// Add a MonthKey before grouping
= Table.AddColumn(Source, "MonthKey",
    each Date.Year([OrderDate]) * 100 + Date.Month([OrderDate]),
    Int64.Type)
```

---

## Technique 4 — Convert Text Columns to Numeric Types

**Impact: High for high-cardinality columns | Effort: Low**

VertiPaq uses two internal encoding strategies:
- **Value encoding** (numeric): stores values directly — very efficient
- **Hash encoding** (text): builds a lookup table of unique strings — far less efficient

When a text column is actually a number in disguise (e.g., order ID `"SO123456"`), strip the prefix and convert:

```m
= Table.TransformColumns(Source, {{
    "OrderNumber",
    each Number.FromText(Text.Replace(_, "SO", "")),
    Int64.Type
}})
```

After converting, set the column's **Default Summarization** to *"Do Not Summarize"* in the model view — this prevents accidental sums of ID values.

High-cardinality columns (unique IDs, transaction codes) benefit the most from this conversion.

---

## Technique 5 — Prefer Power Query Columns Over DAX Calculated Columns

**Impact: Medium | Effort: Low**

DAX calculated columns compress less efficiently than Power Query columns and extend refresh time because they're computed *after* all tables load.

**Prefer (Power Query M)**:
```m
= Table.AddColumn(Source, "GrossMargin",
    each [Revenue] - [Cost],
    type number)
```

**Over (DAX calculated column)**:
```dax
GrossMargin = FactSales[Revenue] - FactSales[Cost]
```

If the source is a relational database, push the calculation into SQL for maximum efficiency:
```sql
SELECT OrderID, Revenue, Cost, (Revenue - Cost) AS GrossMargin
FROM FactSales
```

**When DAX calculated columns ARE the right choice**:
- The formula uses aggregations or measures from other tables
- It requires DAX-only functions (e.g., `PATH()` for parent-child hierarchies)
- It depends on model-level context like security roles or bidirectional relationships

---

## Technique 6 — Disable Load on Staging/Helper Queries

**Impact: Medium | Effort: Very Low**

Power Query queries used only for transformations or to feed other queries should not be loaded into the model. Loading them creates unnecessary tables that waste memory.

To disable:
1. In Power Query Editor, right-click the staging query
2. Uncheck **Enable Load**

The query still executes and feeds its dependent queries — it just won't appear as a table in the model.

---

## Technique 7 — Disable Auto Date/Time

**Impact: Medium–High | Effort: Very Low**

Power BI Desktop's **Auto date/time** option creates a hidden calculated date table for *every* date column in the model. Ten date columns = ten hidden tables, all increasing model size and refresh time.

**Disable for all new files** (recommended):
- File → Options and Settings → Options → Global → Data Load → Time Intelligence
- Uncheck **Auto date/time for new files**

**Disable for the current model**:
- File → Options and Settings → Options → Current File → Data Load
- Uncheck **Auto date/time**

After disabling, create a single shared Date table and connect all date columns to it via relationships. This gives you full calendar intelligence with a fraction of the overhead.

Reference: [Auto date/time guidance](https://learn.microsoft.com/en-us/power-bi/guidance/auto-date-time)

---

## Technique 8 — DirectQuery for Large Fact Tables (Composite Model)

**Impact: Maximum for very large models | Effort: High**

When even aggregated fact tables are still too large, set the storage mode of large fact tables to **DirectQuery** and combine with Import-mode dimension and summary tables in a **Composite model**:

| Table | Storage Mode | Purpose |
|---|---|---|
| Dimensions (Date, Customer, Product) | Import | Fast filter/group context |
| Summarized fact (monthly grain) | Import | Fast summary visuals |
| Full-grain fact | DirectQuery | Drill-through to transaction detail |

This lets summary dashboards run fast from Import aggregates while drill-through pages pull live detail from DirectQuery on demand.

> Carefully evaluate security and performance implications before adopting DirectQuery in production. See [Composite models guidance](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-composite-models).

---

## Prioritized Checklist

Apply in order of impact-to-effort ratio:

| Priority | Technique | Impact | Effort |
|---|---|---|---|
| 1 | Disable Auto Date/Time | Medium–High | Very Low |
| 2 | Disable load on staging queries | Medium | Very Low |
| 3 | Remove unnecessary columns | High | Low |
| 4 | Convert text ID columns to integers | High | Low |
| 5 | Filter rows by time (parameter-driven) | Very High | Low |
| 6 | Move computed columns to Power Query | Medium | Low |
| 7 | Filter rows by entity | High | Medium |
| 8 | Group and summarize fact tables | Up to 99% | Medium |
| 9 | DirectQuery for large fact tables | Maximum | High |

---

## Quick Wins (< 15 minutes)

For immediate relief without architectural changes:

1. **Disable Auto date/time** — 1 minute, no report impact
2. **Disable load on staging queries** — 2 minutes per query
3. **Remove columns not used in any report or relationship** — 10 minutes of audit
4. **Convert text ID columns to integers** — 5 minutes per column

---

## Common Scenarios

### ".pbix file is too large to publish"
Start with Techniques 1, 2, 7, then 3 and 8 if still too large.

### "Reports are slow to load"
Focus on Techniques 4 and 8 — reducing row count has the biggest query performance impact.

### "Dataset refresh takes too long"
Focus on Techniques 5, 6, and row-count reduction (Techniques 3 and 4) — DAX calculated columns and large row counts are the main culprits.

### "I need full transaction detail but the model is too big"
Use Technique 8 (Composite model) — Import aggregates for summaries + DirectQuery for detail.

### "Building a new model — what should I do from the start?"
Apply Techniques 1, 2, 6, 7 proactively. Establish parameterized time filters and a single shared Date table from day one.
