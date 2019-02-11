# neo-rtags
[Rtags](https://github.com/Andersbakken/rtags) client for [Neovim](https://github.com/neovim/neovim).

The client is a clone of [vim-rtags](https://github.com/lyuts/vim-rtags), it's 100% written in Python3
and uses [Python client](https://github.com/neovim/python-client) for Neovim.

## Installation

### Dein

Add following line to your ```~/.config/nvim/init.vim``` file:

```
call dein#add('marxin/neo-rtags')
```

and then run in neovim:

```
:call dein#install()
```

## Mapping

| Mapping | Function name | rc command flags | Description |
|-|-|-|-|
| &lt;Leader&gt;ri | NeoRtagsSymbolInfo | -U | Symbol information |
| &lt;Leader&gt;rc | NeoRtagsFindSubclasses | --class-hierarchy | Find subclasses |
| &lt;Leader&gt;rC | NeoRtagsFindSuperclasses | --class-hierarchy | Find superclasses|
| &lt;Leader&gt;rd | NeoRtagsDiagnose | --diagnose --synchronous-diagnostics | Show diagnostics results in a quickfix window |
| &lt;Leader&gt;rj | NeoRtagsFollowLocation | -f | Follow location |
| &lt;Leader&gt;rl | NeoRtagsListProjects | -w | List projects and select a project |
| &lt;Leader&gt;rf | NeoRtagsFindReferences | -r -e | Find all references |
| &lt;Leader&gt;rn | NeoRtagsFindReferencesByName | -a -R -e | Find all references by a name |
| &lt;Leader&gt;rv | NeoRtagsFindVirtuals| -r -k | Find virtuals |
| &lt;Leader&gt;rp | NeoRtagsJumpToParent | -U --symbol-info-include-parents | Jump to parent |
| &lt;Leader&gt;rw | NeoRtagsRenameSymbol| -r -e --rename | Rename symbol under cursor |

## Code Completion

The plugin registers ```NeoRtagsCompleteFunction``` as ```completefunc``` (i.e. CTRL-X CTRL-U).
If the function is already set, neo-rtags code completion is not set.

## Configuration

| Variable | Description |
|-|-|
| let g:neortagsAlwaysRename = 1 | Always rename symbol and do not ask for confirmation |

## Troubleshooting

The plugin is work in progress. I welcome any requests for new functionality, configuration and
also for seen issue. Please file an issue or write me an email.
