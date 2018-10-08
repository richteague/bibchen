# bibchen

Writing a proposal and need to shrink your bibliography? `bibchen` is here to help!

## Useage

First, clone the respository somewhere and `cd` into the directory. Then if you're using a `.bashrc` file run this in the therminal.

```bash
$ echo alias bibchen="'python $PWD/bibchen.py'" >> ~/.bashrc
$ bash
```

This will allow you to run the script anywhere through:

```bash
$ bibchen path/to/file.tex
```

which will use by default `PDFLaTeX` and `bibtex` to generate the final PDF without altering your manuscript file. There are multiple format options which you can use, a list of which can be found through the `-h` argument,

```bash
$ bibchen -h
```

## Example

A typical bibliography using the `natbib` approach gives something like this:

> <img src="https://github.com/richteague/bibchen/blob/master/test/before.png" width="516" height="224">

`bibchen` will replace the reference section with something much more compact, like this:

> <img src="https://github.com/richteague/bibchen/blob/master/test/after.png" width="512" height="81">

## To Do

1) Check Python3 compatibility.
2) Check for different bibliography styles.
