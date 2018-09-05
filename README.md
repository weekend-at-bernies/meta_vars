# meta_vars
Python code blocks for describing variables

Suppose you have a text file like this:

---
5 34 "this is a string" 1 1fdeadbeef

2 894 "this is another string" 0 1acafebabe

10 120 "this is yet another string" 0 f388bb88bb

---

Wouldn't it be nice to have a way of automagically ascribing meaning to the 5 "variables" in each line?
The python code blocks let you do this!
You create a .xml specification describing your variables ("meta-variables"): type, default value, min/max length etc. etc.
Then feed this .xml specification to this code, along with your raw data, and presto! Auto-magic parsing is done for you, and the data is read into memory for you.
