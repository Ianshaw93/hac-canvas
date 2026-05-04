# hac-canvas

A web canvas for hazardous area classification (DSEAR / IEC 60079-10-1) — drop release-source pins on a plot plan, get zone classifications and a draft DSEAR report out the other end.

> **Status: pre-build.** This repo currently contains only the synthetic demo plant used as the example dataset. The web app, calc engine, and report builder are coming.

## What this will become

```
PDF plot plan  →  pin release sources  →  IEC 60079 zone calc  →  DSEAR docx
                  (substance, grade,        (release rate, Vz, Xz,    (source schedule,
                   hole size, dilution)      zone type per Annex D)    methodology, recs)
```

A single source of truth replacing the current Excel + AutoCAD + Word workflow most small / mid hazardous-area consultancies use today. See [Source Selection Rationale](#) (TBC) for why the demo plant has the source mix it has.

## What's here now

- [`generate_plot_plan.py`](generate_plot_plan.py) — `reportlab` script that emits the synthetic demo plot plan. Reproducible: re-run after editing inputs.
- [`Northgate_Plot_Plan.pdf`](Northgate_Plot_Plan.pdf) — the generated A3 landscape plot plan, 1:154 scale. Fictional bulk storage terminal with 4 release sources (tank vent, pump seal, methanol drain, H₂ compressor flange).

## Regenerating the plot plan

```bash
pip install reportlab
python generate_plot_plan.py
# → Northgate_Plot_Plan.pdf
```

Edit equipment positions, source coords, or scale at the top of the script.

## Demo plant — what's on it

| ID  | Source                  | Substance | Grade     |
|-----|-------------------------|-----------|-----------|
| S1  | Tank breather vent      | CH₄       | primary   |
| S2  | Pump shaft seal         | C₃H₈      | primary   |
| S3  | Open drain tundish      | CH₃OH     | primary   |
| S4  | Compressor flange       | H₂        | secondary |

Coordinates and substance properties chosen so each source exercises a different cell of the calc-coverage matrix (gas jet vs. pool evaporation, primary vs. secondary grade, IIA vs. IIC equipment, range of release rates and zone radii).

## Roadmap

- [ ] **Canvas** — Next.js + `react-pdf` page, click-to-pin, scale calibration.
- [ ] **Calc engine** — FastAPI service, IEC 60079-10-1 simplified per Annex B/C/D.
- [ ] **Report builder** — `python-docx` section-pattern builder emitting DSEAR Assessment doc.
- [ ] **Substance DB** — initial 4 substances (CH₄, C₃H₈, CH₃OH, H₂); extensible JSON.
- [ ] **Mobile-responsive** site-capture flow.
- [ ] **Public deployment** — Vercel (frontend) + Railway (backend).

## Scope discipline

This is a demo of the *pattern*. The calc engine implements the simplified Annex B / C / D method. It is **not** a substitute for a competent engineer's full classification, and it is **not** a replacement for tools like DNV Phast for complex consequence modelling. The point is to show what one source-of-truth canvas → calc → report can look like.

## Licence

MIT — see [LICENSE](LICENSE).

---

Built as the worked example for [Scaling Smiths](https://scalingsmiths.com)' YouTube content on AI-driven engineering tooling for safety consultancies.
