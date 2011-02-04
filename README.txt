Source-tree layout
------------------

At the top-level things are fairly straight-forward.

The two main scripts of interest are ``cplr``, which invokes the compiler proper and ``run``, which provides infrastructure tools like running the tests.

Any file with the extension ".txt" can be assumed to be reStructuredText suitable for processing by docutils.

``#`` - Refers to the project root (the directory that contains this file)

``#/src`` - Contains all the project sources. More explanations are available for each of the components.

``#/doc`` - Contains documentation artifacts that get included in the final composition and directives on how to assemble the documentation from the source.

``#/build`` - Where built artifacts get placed. For example the PDF of the final composed documentation. The directory will never be placed under version control since its contents can always be re-created from the source tree contents.

``#/toolchain`` - A self contained environment. It will contain any third party tools or libraries needed to run CPLR itself or generate the documentation. By including the toolchain under version control anyone who checks out a working branch immediately has a working environment without needing to install software on their systems.

------

A few cool things to note:

* The source provides a library for bootstrapping a compiler front end
* The source is written in "reverse literate style" That is, The code reads somewhat like prose but out of order, the code can be executed as a valid python library. A tool can be run on the code to extract a document (via ReStructured text). This idea was inspired by "Physically Based Rendering" http://www.pbrt.org/ - a document that builds a working compiler library step by step could be a great teaching tool to follow along and build your own compiler
