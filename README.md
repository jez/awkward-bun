# 11-411 Natural Language Processing

![awkward bun](https://athrice.files.wordpress.com/2015/04/scrunchy-bun.png)


## Setup

### Python Project Setup

Make sure you have Python 3 installed.

First things first, you'll need to install the required project dependencies. If
you aren't familiar with `virtualenv` in Python, I'd recommend installing
[virtualenvwrapper]. Follow the instructions [here][vew-install] to install it.
Be sure to follow the instructions under "Basic Installation" as well as "Shell
Startup File" (you'll have to make some changes to your `~/.bashrc` file).

After you're relaunched your shell, run this to create a virtualenv for our
project:

```console
$ mkvirtualenv awkward-bun
```

You'll be placed into a Python virtual environment for our project, named
"awkward-bun". To exit this environment at any time, run

```console
$ deactivate
```

To re-enter the virtual environment, run

```console
$ workon awkward-bun
```

As a general rule, any time you're developing code for this project, **you
should make sure you've run `workon ...`** so that all your changes will be
reflected in the virtualenv.

### Python Dependencies and NLTK

While in your virtualenv, to install the python dependencies, run

```console
$ pip install -r requirements.txt
```

from the top-level of the project. You may have to use `sudo` if the
installation fails.

Now we'll need to install the supplementary NLTK data:

```console
$ python -m nltk.downloader -d ./nltk_data all
```

This installs the "all" datasets from NLTK to the `nltk_data` folder in the top
level of our project (creating this folder if necessary).


### Stanford Parser and NER Tagger Setup

The Stanford Parser and NER Tagger are a Java dependencies, so we have to have
to install their components separately, (but we can still interface with them
through NLTK's Python frontend).

First, follow [the links listed here][third-party] to download the required
files. (You can ignore the parts about environment variables). **You only need
the parser and NER tagger downloads.**

> **Note for OS X users**: you can skip all the download steps by just running
>
>     $ brew install stanford-parser stanford-ner
>
> which will put the files you need in `/usr/local/opt/stanford-parser/libexec`
> and `/usr/local/opt/stanford-ner/libexec`.

Once you have these files, you'll need to copy some of them into the Git repo
(they will be properly ignored, so you don't have to risk accidentally
committing them).

| File you downloaded                   | Place in this repo                   |
| -------------------                   | ------------------                   |
| `stanford-parser.jar`                 | `jars/`                              |
| `stanford-parser-3.5.2-models.jar`    | `jars/`                              |
| `edu/stanford/nlp/models/lexparser/*` | `edu/stanford/nlp/models/lexparser/` |
| `stanford-ner.jar`                    | `jars/`                              |
| `classifiers/*`                       | `classifiers/`                       |

You can find all of the `edu/stanford/nlp/models/lexparser` files by extracting
them from the models JAR file:

```console
$ jar xf stanford-parser-3.5.2-models.jar
```

## Running

Make sure you have properly set up the system. From there, there are two entry
points: the `ask` module and the `answer` module.


### `./ask`

```bash
$ ./ask
usage: ./ask <article> <nquestions>

$ ./ask ./external/data/set1/a1.txt 10
Is the sky blue?
...

# alternatively, run with debugging enabled:
$ DEBUG=1 ./ask ./external/data/set1/a1.txt 10
... Lots of debugging output ...

Summary:
...

[3.50] Is the sky blue?
...
```

### `./answer`

TODO!


## Members

- Annie Cheng
- Richard Fan
- Brian Li
- Jake Zimmerman

## License

MIT License. See LICENSE.

[virtualenvwrapper]: https://virtualenvwrapper.readthedocs.org/en/latest/
[vew-install]: http://virtualenvwrapper.readthedocs.org/en/latest/install.html#basic-installation
[third-party]: https://github.com/nltk/nltk/wiki/Installing-Third-Party-Software#stanford-tagger-ner-tokenizer-and-parser
