#!/usr/bin/env python3
"""
Genera index.html a partir de un notebook ya ejecutado.

Busca, para fig1/fig2/fig3, la celda de código donde se define la figura
(ej. "fig1 = px.bar(") Y donde se llama a su .show() en la MISMA celda
(ej. "fig1.show()"). Esto evita confundirla con la celda final del
notebook que solo hace fig1.show()/fig2.show()/fig3.show() juntas.

Uso:
    python build_dashboard.py <notebook_ejecutado.ipynb> <salida.html>
"""
import json
import re
import sys


def find_fig_html(nb, fig_name):
    for cell in nb["cells"]:
        if cell.get("cell_type") != "code":
            continue
        src = "".join(cell.get("source", []))
        if f"{fig_name} = px." in src and f"{fig_name}.show()" in src:
            for out in cell.get("outputs", []):
                data = out.get("data", {})
                if "text/html" in data:
                    html = "".join(data["text/html"])
                    return html
    return None


def extract_plot(html):
    m = re.search(
        r'Plotly\.newPlot\(\s*"([^"]+)",\s*(\[.*\])\s*,\s*(\{.*\})\s*,\s*(\{.*\})\s*\)',
        html,
        re.S,
    )
    if not m:
        return None
    _divid, data, layout, _config = m.groups()
    return data, layout


TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Dashboard: Expectativa de Vida (WHO)</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  :root {{
    --bg: #0f172a;
    --card-bg: #ffffff;
    --text: #1e293b;
    --muted: #64748b;
    --accent: #2563eb;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 240px, #f1f5f9 240px);
    color: var(--text);
  }}
  header {{ padding: 40px 24px 24px; max-width: 1100px; margin: 0 auto; color: #f8fafc; }}
  header h1 {{ margin: 0 0 6px; font-size: 1.8rem; }}
  header p {{ margin: 0; color: #cbd5e1; font-size: 0.95rem; }}
  main {{ max-width: 1100px; margin: 0 auto; padding: 0 24px 60px; display: grid; gap: 24px; }}
  .card {{ background: var(--card-bg); border-radius: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); padding: 8px 8px 4px; }}
  .plot {{ width: 100%; }}
  footer {{ max-width: 1100px; margin: 0 auto; padding: 0 24px 40px; color: var(--muted); font-size: 0.8rem; }}
  a {{ color: var(--accent); }}
</style>
</head>
<body>
<header>
  <h1>\U0001F30D Dashboard: Expectativa de Vida (WHO)</h1>
  <p>Programación para la Ciencia de Datos · Sebastián Gonzalez, Ignacio Cerda, Jesús Morán</p>
  <p style="font-size:0.75rem;color:#94a3b8;">Generado automáticamente desde notebook.ipynb</p>
</header>
<main>
  <div class="card"><div id="plot1" class="plot"></div></div>
  <div class="card"><div id="plot2" class="plot"></div></div>
  <div class="card"><div id="plot3" class="plot"></div></div>
</main>
<footer>
  Fuente de datos: Kaggle — "Life Expectancy WHO Updated" (lashagoch). Gráficos generados con Plotly a partir del análisis del notebook.
</footer>
<script>
  var config = {{responsive: true, displaylogo: false}};
  Plotly.newPlot("plot1", {data1}, {layout1}, config);
  Plotly.newPlot("plot2", {data2}, {layout2}, config);
  Plotly.newPlot("plot3", {data3}, {layout3}, config);
</script>
</body>
</html>
"""


def main():
    if len(sys.argv) != 3:
        print("Uso: python build_dashboard.py <notebook.ipynb> <salida.html>")
        sys.exit(1)

    nb_path, out_path = sys.argv[1], sys.argv[2]

    with open(nb_path, encoding="utf-8") as f:
        nb = json.load(f)

    figs = {}
    for name in ["fig1", "fig2", "fig3"]:
        html = find_fig_html(nb, name)
        if html is None:
            print(f"ERROR: no se encontró output para {name}. "
                  f"¿El notebook se ejecutó y guardó su output?")
            sys.exit(1)
        result = extract_plot(html)
        if result is None:
            print(f"ERROR: no se pudo extraer data/layout de {name}.")
            sys.exit(1)
        figs[name] = result

    html_out = TEMPLATE.format(
        data1=figs["fig1"][0], layout1=figs["fig1"][1],
        data2=figs["fig2"][0], layout2=figs["fig2"][1],
        data3=figs["fig3"][0], layout3=figs["fig3"][1],
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)

    print(f"OK: {out_path} generado ({len(html_out)} bytes)")


if __name__ == "__main__":
    main()
