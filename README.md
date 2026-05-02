# skill-optimize-data-models-power-bi

A Claude Code skill that guides you through optimizing Power BI Import data models — reducing file size, speeding up reports, and cutting refresh times.

## What it does

When you describe a Power BI performance problem, Claude reads this skill and gives you **prioritized, actionable recommendations** with ready-to-use Power Query (M) and SQL code. No generic advice — it asks the right diagnostic questions first, then focuses on what matters for your specific situation.

**Benchmark:** 100% assertion pass rate vs 75% without the skill. The biggest difference is in slow-report scenarios, where the skill provides the explicit symptom-to-cause diagnosis and `Table.Group` aggregation code that Claude doesn't reliably produce on its own.

## Techniques covered

| # | Technique | Impact | Effort |
|---|---|---|---|
| 1 | Disable Auto Date/Time | Medium–High | Very Low |
| 2 | Disable load on staging queries | Medium | Very Low |
| 3 | Remove unnecessary columns | High | Low |
| 4 | Convert text ID columns to integers | High | Low |
| 5 | Filter rows by time (parameter-driven) | Very High | Low |
| 6 | Move computed columns to Power Query | Medium | Low |
| 7 | Filter rows by entity | High | Medium |
| 8 | Group and summarize fact tables | Up to 99% | Medium |
| 9 | DirectQuery + Composite model | Maximum | High |

## Triggers automatically when you say things like

- *"My .pbix is 800 MB and I can't publish it"*
- *"My Power BI report takes 10 seconds to load"*
- *"Dataset refresh is taking 45 minutes"*
- *"Building a new model with a 100M row SQL Server table — what are best practices?"*
- *"How do I reduce VertiPaq model size?"*
- *"Should I use DirectQuery or Import mode?"*

## Installation

### Option 1 — Claude Code CLI

```bash
claude skill install https://github.com/Albopbix/skill-optimize-power-bi
```

### Option 2 — Manual

1. Clone or download this repo
2. Copy `SKILL.md` into your Claude skills directory:
   - **macOS/Linux**: `~/.claude/skills/skill-optimize-data-models-power-bi/`
   - **Windows**: `%USERPROFILE%\.claude\skills\skill-optimize-data-models-power-bi\`

## Usage

Just describe your Power BI problem naturally. The skill activates automatically:

```
User: My Power BI report is super slow and the .pbix is almost 1 GB.
      I have a sales fact table with 50M rows going back to 2010.

Claude: [Diagnoses the model, gives prioritized recommendations,
         provides Power Query M code to fix each issue]
```

## Code examples included

The skill ships with ready-to-run Power Query (M) and SQL snippets for each technique, such as:

**Parameter-driven time filter:**
```m
let
    CutoffDate = Date.AddYears(Date.From(DateTime.LocalNow()), -HistoryYears),
    Source     = Sql.Database("server", "db"),
    FactSales  = Source{[Schema="dbo", Item="FactSales"]}[Data],
    Filtered   = Table.SelectRows(FactSales, each [OrderDate] >= CutoffDate)
in
    Filtered
```

**Aggregate fact table to reduce rows by up to 99%:**
```m
Grouped = Table.Group(
    FactSales,
    {"OrderDate", "CustomerID", "ProductID"},
    {
        {"TotalRevenue",  each List.Sum([Revenue]),  type number},
        {"TotalQuantity", each List.Sum([Quantity]), type number},
        {"OrderCount",    each Table.RowCount(_),    type number}
    }
)
```

**Convert text ID to integer (VertiPaq value encoding):**
```m
= Table.TransformColumns(Source, {{
    "OrderNumber",
    each Number.FromText(Text.Replace(_, "SO", "")),
    Int64.Type
}})
```

## Source

Built from Microsoft's official guidance:
[Data reduction techniques for Import modeling — Microsoft Learn](https://learn.microsoft.com/en-us/power-bi/guidance/import-modeling-data-reduction)

## License

MIT
