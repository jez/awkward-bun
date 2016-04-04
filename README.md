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
$ mkvirtualenv --python=$(which python3) awkward-bun
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


### Stanford Parser Setup

The Stanford Parser is a Java dependency, so we have to have to install it's
components separately, (but we can still interface with them through NLTK's
Python frontend).

First, follow [the links listed here][third-party] to download the required
files. (You can ignore the parts about environment variables).

> **Note for OS X users**: you can skip all the download steps by just running
>
>     console
>     $ brew install stanford-parser
>
> which will put the files you need in `/usr/local/opt/stanford-parser/libexec`.

Once you have these files, you'll need to copy some of them into the Git repo
(they will be properly ignored, so you don't have to risk accidentally
committing them).

| File you downloaded                   | place in this repo                   |
| -------------------                   | ------------------                   |
| `stanford-parser.jar`                 | `jars/`                              |
| `stanford-parser-3.5.2-models.jar`    | `jars/`                              |
| `edu/stanford/nlp/models/lexparser/*` | `edu/stanford/nlp/models/lexparser/` |

You can find all of the `edu/stanford/nlp/models/lexparser` files by extracting
them from the models JAR file:

```console
$ jar xf stanford-parser-3.5.2-models.jar
```


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
