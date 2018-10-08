"""
Make a smaller bibliography for all those proposals. To run simply use:

> python bibchen.py path/to/file.tex

Making sure that the bibfile is in there too. This should generate the PDF with
PDFLaTeX after running bibtex to get the citations correct, but then replacing
the old bibliography with a shorter version.

TODO:

1) Check this works for other common bibstyles.
2) Allow for changing number of authors in the references.
3) Allow for changes to a) fontsize, b) separating symbol.

"""

import os
import sys
import subprocess

if __name__ == '__main__':

    # Read in the files.
    cdir = os.getcwd()

    try:
        path = sys.argv[1]
        if '/' not in path:
            file = path
            path = './'
        else:
            file = path.split('/')[-1]
            path = path.replace(file, '')
    except IndexError:
        file = [fn for fn in os.listdir('./') if fn.endswith('.tex')][0]
        path = './'

    if file.endswith('.tex'):
        file = file[:-4]
    os.chdir('%s' % path)

    # Keep track of which files are originally there.
    files = [fn for fn in os.listdir('./')]

    # Copy the original tex file to save.
    with open('temp.sh', 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('cp %s.tex %s_temp.tex\n' % (file, file))

    # Check if there's a .bbl file. If not, make one.
    if not os.path.isfile('%s.bbl' % file):
        with open('temp.sh', 'a') as f:
            f.write('pdflatex %s\n' % file)
            f.write('bibtex %s\n' % file)

    # Create appropriate files.
    os.chmod('./temp.sh', 0o755)
    subprocess.call('./temp.sh')
    os.system('rm temp.sh')

    # Read in the temporary tex file and the bbl file.
    with open('%s.tex' % file, 'r') as f:
        tex = f.readlines()
    with open('%s.bbl' % file, 'r') as f:
        bbl = f.readlines()
    bbl = ''.join(bbl)

    # Find the bibliography section.
    for l, line in enumerate(tex):
        if r'\bibliography{' in line:
            break
    bib = line.split('{')[1].split('}')[0]
    tex[l] = r'\newsavebox\mytempbib' + \
             r'\savebox\mytempbib{\parbox{\textwidth}' + \
             r'{\bibliography{%s}}}' % bib + '\n'

    # Cycle through the citation keys and replace them.
    bib_items = [item for item in bbl.split(r'\bibitem')[1:]]
    for b in range(len(bib_items)):
        bib_items[b] = bib_items[b].replace(r'\newblock', '')
        bib_items[b] = bib_items[b].replace(r'\end{thebibliography}', '')

    # Write the new reference section.
    ref = r'\vspace{0.2cm}\noindent\textbf{References:} '
    for b, bib_item in enumerate(bib_items):

        # Format is \bibitem[{Surname} A. B. {Surname} A. B. ...]{citekey}.
        citation, citekey = bib_item.split(']')
        citation = citation[2:].split(')')[0] + ')'
        citation = citation.replace('}', '').replace('{', '')
        citekey = citekey[1:].split('}')[0]

        # Search for the date.
        full_ref = bib_item.split(']')[1].replace('{' + citekey + '}', '')
        for c, char in enumerate(full_ref):
            if char.isdigit():
                break
        full_ref = citation.split('(')[0] + ' ' + full_ref[c:]
        if b > 0:
            ref += r' $\cdot$ '
        ref += full_ref

    # Replace the reference section.
    ref = ref.replace('\n', '')
    tex.insert(l+1, ref)

    # Rewrite the tex file.
    with open('%s.tex' % file, 'w') as f:
        for line in tex:
            f.write(line)

    # Compile the new PDF.
    with open('temp.sh', 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('pdflatex %s.tex\n' % file)
        f.write('bibtex %s\n' % file)
        f.write('pdflatex %s.tex\n' % file)
        f.write('pdflatex %s.tex\n' % file)
        f.write('mv %s_temp.tex %s.tex\n' % (file, file))
    os.chmod('./temp.sh', 0o755)
    subprocess.call('./temp.sh')
    os.system('rm temp.sh')

    # Clean up the intermediate files.
    files += ['%s.pdf' % file]
    for fn in os.listdir('./'):
        if fn not in files:
            os.system('rm %s' % fn)

    # Change back to original directory.
    os.chdir('%s' % cdir)
