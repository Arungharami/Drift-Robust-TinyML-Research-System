from pathlib import Path
def test_figure_index_links_source_csvs():
    text=Path("paper/FIGURE_INDEX.md").read_text(); assert "Source CSV" in text and "results/figures/sources/" in text
