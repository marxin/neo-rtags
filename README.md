# neo-rtags
Rtags client for neovim

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
