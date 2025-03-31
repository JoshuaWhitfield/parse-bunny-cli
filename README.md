# parse-bunny-cli
This is a data collection cli for AI model training and development

<h1>Getting Started:</h1>
<p>clone the repository and download the following dependencies:</p>
```bash
   _
    python -m pip install requests

    python -m pip install beautifulsoup4

    python -m pip install validators
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
  _
   $ data <url> -collect -template[std] -search-engine["<keyword1>", "<keyword2>"]
   $ data <url> -collect -template[std] -search-engine[]
```

<h4>description</h4>
<p>visits a url and scrapes every element that contains a keyword. 
when ommitting keywords from the `-search-engine` flag, all content is scraped.</p>
<br />

<h1>Inputs</h1>
<br />
<h3>up arrow-key</h3>
<h4>description</h4>
<p>displays previous command, and is ready for execution.</p>

<h3>press CTRL + C to exit<h3>
