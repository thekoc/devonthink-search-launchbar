# DEVONthink Launchbar Search Tool
## What does it do?
The tool aims to let you search and navigate through DEVONthink effectively. It learns from your habit so that the items get hitted most will show at the top.

## How does it work?
Just enter the keyword and it will do a live and prefix search then nicely present the results for you.
![Search Result](screenshots/search-result.png)

### Modifier keys
If it is not a group:
- `⌘ + Enter` to reveal that item in DEVONthink
- `⇧ + Enter` to reveal that item in Finder
- `⌥ + Enter` to open that item externally

If it is a group:
- `⌘ + Enter` to reveal that item in DEVONthink
- `⌥ + Enter` to navigate through that group in Launchbar

Note that if you are already in "navigation mode", just press enter and you can navigate that group, press `⌥ + Enter` to open that group in DEVONthink.

### Excluded tag
If you tag a file/group `exclude-from-launchbar`, it will not be shown in the result.


## Config
You can adjust all those values in the config file `config.py`.

![Config](screenshots/config.png)

Defualt values:

```python
a = 0.8
b = 0.5
frequency_weight = 2
excluded_tag = 'exclude-from-launchbar'
max_result_num = 80
```

The `max_result_num` option can be set to `None` so that all the results will be presented in LaunchBar. Note that too many results may cause performance issue!

## More details
### Frequency score
Except for the search score given by DEVONthink, the tool will adjust that score based on the frequency you open items.

`final_score = search_score + weight * frequency_score`


How do the tool calcuate the `frequency_score`?

Every time you choose a item, it update the frequency score of every item appears using the following formula.

`frequency_score = old_score * a + (1 - a) * (1 if is_chosen else 0)`

The initial value is 0. The `frequency_score` is set to `b` (in config.py) the first time it is selected. Later if it is not selected, the score will decrease according the the formula. But it will not drop below `b`.

### Search query
The query template used is `name:({}) tags!={}`. So only the name is searched and the specific tag is excluded (default to `exclude-from-launchbar`). In more detail, each keyword entered is prepended with a `~`. For example, if the text you type in LaunchBar is `hello world`, then the actual query will be `name:(~hello ~world) tags!=exclude-from-launchbar`.
