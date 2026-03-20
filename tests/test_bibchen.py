import os
import shutil
import subprocess
import sys
import textwrap

import pytest

from bibchen import format_references

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TEST_DIR = os.path.join(os.path.dirname(__file__), '..', 'test')

# Minimal .bbl fixture matching the natbib/AAS label format:
#   \bibitem[{Author...}(year)]{citekey}
FIXTURE_BBL = textwrap.dedent(r"""
    \begin{thebibliography}{}

    \bibitem[{Teague} \& {Foreman-Mackey}(2018)]{Teague_Foreman-Mackey_2018}
    {Teague}, R., \& {Foreman-Mackey}, D.\ 2018, Research Notes of the AAS, 2, 173

    \bibitem[{Teague} {et~al.}(2018)]{Teague_ea_2018}
    \newblock {Teague}, R., {Bae}, J., {Bergin}, E.~A., {et~al.}\ 2018, ApJL, 860, L12

    \end{thebibliography}
""")


def has_command(name):
    return shutil.which(name) is not None


requires_latex = pytest.mark.skipif(
    not (has_command('pdflatex') and has_command('bibtex')),
    reason='pdflatex and bibtex must be available',
)


# ---------------------------------------------------------------------------
# Unit tests for format_references()
# ---------------------------------------------------------------------------

class TestFormatReferences:

    def test_returns_string(self):
        result = format_references(FIXTURE_BBL, 'normalsize', 'References', r' $\cdot$ ')
        assert isinstance(result, str)

    def test_wrapped_in_group(self):
        result = format_references(FIXTURE_BBL, 'normalsize', 'References', r' $\cdot$ ')
        assert result.startswith(r'\begingroup')
        assert result.endswith(r'\endgroup')

    def test_fontsize_included(self):
        for size in ('footnotesize', 'small', 'scriptsize'):
            result = format_references(FIXTURE_BBL, size, 'References', r' $\cdot$ ')
            assert r'\%s' % size in result

    def test_title_included(self):
        result = format_references(FIXTURE_BBL, 'normalsize', 'My References', r' $\cdot$ ')
        assert r'\textbf{My References\quad}' in result

    def test_symbol_between_entries(self):
        symbol = r' $\star$ '
        result = format_references(FIXTURE_BBL, 'normalsize', 'References', symbol)
        assert symbol in result

    def test_symbol_not_at_start(self):
        # The separator should not appear before the first entry.
        symbol = r' $\cdot$ '
        result = format_references(FIXTURE_BBL, 'normalsize', 'References', symbol)
        header_end = result.index(r'\textbf{References\quad}') + len(r'\textbf{References\quad}')
        assert not result[header_end:].startswith(symbol)

    def test_author_names_present(self):
        result = format_references(FIXTURE_BBL, 'normalsize', 'References', r' $\cdot$ ')
        assert 'Teague' in result

    def test_year_present(self):
        result = format_references(FIXTURE_BBL, 'normalsize', 'References', r' $\cdot$ ')
        assert '2018' in result

    def test_newblock_stripped(self):
        result = format_references(FIXTURE_BBL, 'normalsize', 'References', r' $\cdot$ ')
        assert r'\newblock' not in result

    def test_end_thebibliography_stripped(self):
        result = format_references(FIXTURE_BBL, 'normalsize', 'References', r' $\cdot$ ')
        assert r'\end{thebibliography}' not in result

    def test_no_newlines_in_entries(self):
        result = format_references(FIXTURE_BBL, 'normalsize', 'References', r' $\cdot$ ')
        # Everything after \begingroup header lines should have no embedded newlines
        # within each reference entry (they are joined into one line).
        entries_part = result.split(r'\noindent\textbf')[1]
        # Each entry should not have a bare newline that would break the inline layout.
        assert '\n' not in entries_part

    def test_single_entry_no_symbol(self):
        single = textwrap.dedent(r"""
            \begin{thebibliography}{}
            \bibitem[{Teague} \& {Foreman-Mackey}(2018)]{Teague_Foreman-Mackey_2018}
            {Teague}, R.\ 2018, Research Notes of the AAS, 2, 173
            \end{thebibliography}
        """)
        symbol = r' $\cdot$ '
        result = format_references(single, 'normalsize', 'References', symbol)
        assert symbol not in result


# ---------------------------------------------------------------------------
# Integration test — runs the full CLI on the test fixtures
# ---------------------------------------------------------------------------

@requires_latex
def test_integration_produces_pdf(tmp_path):
    """Run bibchen on test/main.tex and verify a PDF is produced."""
    # Copy test fixtures into a temp directory so we don't pollute the repo.
    for fname in ('main.tex', 'bibliography.bib', 'aas.bst'):
        shutil.copy(os.path.join(TEST_DIR, fname), tmp_path / fname)

    tex_path = str(tmp_path / 'main.tex')
    result = subprocess.run(
        [sys.executable, '-m', 'bibchen', tex_path],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / 'main.pdf').exists()


@requires_latex
def test_integration_original_tex_restored(tmp_path):
    """The original .tex file must be unchanged after bibchen runs."""
    for fname in ('main.tex', 'bibliography.bib', 'aas.bst'):
        shutil.copy(os.path.join(TEST_DIR, fname), tmp_path / fname)

    tex_path = str(tmp_path / 'main.tex')
    with open(tex_path) as f:
        original = f.read()

    subprocess.run(
        [sys.executable, '-m', 'bibchen', tex_path],
        capture_output=True,
    )

    with open(tex_path) as f:
        restored = f.read()

    assert restored == original


@requires_latex
def test_integration_noclean_keeps_bbl(tmp_path):
    """With --noclean, intermediate files including the .bbl should remain."""
    for fname in ('main.tex', 'bibliography.bib', 'aas.bst'):
        shutil.copy(os.path.join(TEST_DIR, fname), tmp_path / fname)

    subprocess.run(
        [sys.executable, '-m', 'bibchen', str(tmp_path / 'main.tex'), '--noclean'],
        capture_output=True,
    )

    assert (tmp_path / 'main.bbl').exists()
