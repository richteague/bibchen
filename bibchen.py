"""
Make a smaller bibliography for all those proposals. To run simply use:

> bibchen path/to/file.tex

"""

import os
import argparse
import subprocess

# Define the acceptable fontsizes. TODO: Accept a number too?
fontsizes = ['Huge', 'huge', 'LARGE', 'Large', 'large', 'normalsize',
             'small', 'footnotesize', 'scriptsize', 'tiny']

if __name__ == '__main__':

    # Parse the arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('path',
                        help='path to .tex file')
    parser.add_argument('-fontsize', default='normalsize',
                        help='Font size for the bibliography. Default is ' +
                             '"normalsize".')
    parser.add_argument('-latex', default='pdflatex',
                        help='LaTeX engine used to generate PDF. Default is' +
                             ' "pdflatex".')
    parser.add_argument('-title', default='References',
                        help='Heading name used for the bibliography. Use' +
                             ' underscores in place of spaces. Default is ' +
                             '"References".')
    parser.add_argument('-symbol', default='cdot',
                        help='Symbol used to break references. Default is ' +
                             '"cdot".')
    parser.add_argument('--noclean', action='store_true',
                        help='Do not clean up intermediate files.')
    parser.add_argument('--verbose', action='store_true',
                        help='Show messages from PDF generation.')
    args = parser.parse_args()

    if not args.verbose:
        stdout = open(os.devnull, 'wb')
        stderr = subprocess.STDOUT
    else:
        stdout = None
        stderr = None

    # Get the directory and filename.
    if '/' not in args.path:
        file = args.path
        path = './'
    else:
        file = args.path.split('/')[-1]
        path = args.path.replace(file, '')
    if file.endswith('.tex'):
        file = file[:-4]
    os.chdir('%s' % path)

    # Check the fontsize.
    fontsize = args.fontsize
    if fontsize not in fontsizes:
        raise ValueError("Unknown fontsize.")

    # Check the symbol for reference breaks.
    symbol = args.symbol.replace(r'\\', '')
    symbol = r' $\%s$ ' % symbol

    # Keep track of which files are in the CWD.
    cdir = os.getcwd()
    files = [fn for fn in os.listdir('./')]

    # Copy the original tex file to save.
    with open('temp.sh', 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('cp %s.tex %s_temp.tex\n' % (file, file))

    # Check if there's a .bbl file. If not, make one.
    if not os.path.isfile('%s.bbl' % file):
        with open('temp.sh', 'a') as f:
            f.write('%s %s\n' % (args.latex, file))
            f.write('bibtex %s\n' % file)

    # Create appropriate files.
    os.chmod('./temp.sh', 0o755)
    subprocess.call('./temp.sh', stdout=stdout, stderr=stderr)
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
    ref = r'\begingroup' + '\n'
    ref += r'\%s' % fontsize + '\n'
    ref += r'\vspace{0.2cm}' + '\n'
    ref += r'\paragraph{%s} ' % args.title.replace('_', ' ')
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
            ref += symbol
        ref += full_ref.replace('\n', '')
    ref += r'\endgroup'

    # Replace the reference section and rewrite the file.
    tex.insert(l+1, ref)
    with open('%s.tex' % file, 'w') as f:
        for line in tex:
            f.write(line)

    # Compile the new PDF.
    with open('temp.sh', 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('%s %s\n' % (args.latex, file))
        f.write('bibtex %s\n' % file)
        f.write('%s %s\n' % (args.latex, file))
        f.write('%s %s\n' % (args.latex, file))
        f.write('mv %s_temp.tex %s.tex\n' % (file, file))
    os.chmod('./temp.sh', 0o755)
    subprocess.call('./temp.sh', stdout=stdout, stderr=stderr)
    os.system('rm temp.sh')

    # Clean up the intermediate files.
    if not args.noclean:
        files += ['%s.pdf' % file]
        for fn in os.listdir('./'):
            if fn not in files:
                os.system('rm %s' % fn)

    # Change back to original directory.
    os.chdir('%s' % cdir)
