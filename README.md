# bibchen

Writing a proposal and need to shrink your bibliography? `bibchen` is here to help!

## Useage

### Installation

First, clone the respository somewhere and `cd` into the directory. Then if you're using a `.bashrc` file run this in the therminal.

```bash
$ echo 'alias bibchen="python $PWD/bibchen.py"' >> ~/.bashrc
$ bash
```

### Running

From anywhere you should be able to run:

```bash
$ bibchen path/to/file.tex
```

which will use by default `PDFLaTeX` and `bibtex` to generate the final PDF without altering your manuscript file. There are multiple format options which you can use, a list of which can be found through the `-h` argument,

```bash
$ bibchen -h
```

### Troubleshooting

A failure might occur if you do not have `pdflatex` or `bibtex` commands available via the command line. Check that your `PATH` points to the right location. For some older MacOS versions, an update might have changed this ([for example](https://superuser.com/questions/982647/cannot-find-pdflatex-after-upgrade-to-mac-os-x-10-11-el-capitan)).

A good first try would be something like:

```bash
$ echo 'export PATH="$PATH:/Library/TeX/Root/bin/x86_64-darwin/"' >> ~/.bashrc
```

## Example

A typical bibliography using the `natbib` approach gives something like this:

> <img src="https://github.com/richteague/bibchen/blob/master/test/before.png" width="570" height="526">

`bibchen` will replace the reference section with something much more compact, like this:

> <img src="https://github.com/richteague/bibchen/blob/master/test/after.png" width="570" height="400">

## To Do

1) Check Python3 compatibility.
