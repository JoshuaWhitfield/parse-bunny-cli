# parse-bunny-cli
This is a data collection cli for AI model training and development

<h1>Getting Started:</h1>
<p>clone the repository and download the following dependencies:</p>

```bash
    # $ clone the repository

    $ python -m venv parse-bunny

    $ parse-bunny\Scripts\activate

    $ python -m pip install requests

    $ python -m pip install beautifulsoup4
fx
    $ python -m pip install validators

    $ python -m pip install redis
```

<h1>Commands:</h1>
<br />
<h3>clear</h3>
<h4>description:</h4>
<p>clears the terminal screen</p>
<br />
<h3>data</h3>
<h4>usage:</h4>

```bash 
   $ data <url> -collect["king", "lebron", "james"]
   $ data <url> -collect["lebron"] -parse[]
```

<h4>description</h4>
<p>visits a url and scrapes every element that contains a keyword. 
when ommitting keywords from the `-collect` flag, all content is scraped. when ommitting the path from the `-parse` flag, the built in parser is used. any custom parsers must contain the following function: ```python 
    # its best practice to create a class above the main parser function #
    class Parser:
        def __init__(self):
            # your code here
            self.input = ""
            self.output = ""

        def set_input(self, new_input):
            self.input = new_input

        def get_output(self):
            return self.output
        # ...
        
        def parse(self):
            # your parsing function here

    def run_parser(input):
        # your custom parser code #
        parser = Parser()
        parser.set_input(input)
        parser.parse()
        return self.get_output()

```
the run_parser function should always take in one parameter which is a string and should always be named `run_parser`.
</p>
<br />

<h1>Inputs</h1>
<br />
<h3>up arrow-key</h3>
<h4>description</h4>
<p>displays previous command, and is ready for execution.</p>

<h3>press CTRL + C to exit<h3>

