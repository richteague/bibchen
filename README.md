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

## Example

A typical bibliography using the `natbib` approach gives something like this:

---
![alt-text](https://github.com/richteague/bibchen/blob/master/test/before.png "Standard bibliography.")
---

`bibchen` will replace the reference section with something much more compact, like this:

---
![alt-text](https://github.com/richteague/bibchen/blob/master/test/after.png "Shrunken bibliography.")
---

## To Do

1) Check Python3 compatibility.
2) Check for different bibliography styles.
3) Allow for user-specified fontsize, titles and reference breaks
