#compdef nicole
# https://zsh.sourceforge.io/Doc/Release/Completion-System.html#Completion-Functions
_lyrics-site()
{
    _values "lyrics site" \
        'genius[use only genius.com]' \
        'azlyrics[use only azlyrics.com]' \
        'all[use all supported sites (default)]'
}

_nicole()
{
    # each argument is
    # n:message:action
    # option[description]:message:action
    # # -s allow stacking, eg -inr
    _arguments -s \
        {--directory,-d}'[process directory]':directory:_directories \
        {--file,-f}'[process file]':file:_files \
        {--recursive,-r}'[go through directories recursively]' \
        '--silent[silent]' \
        {--ignore-history,-i}'[ignore history]' \
        {--no-history,-n]}'[do not write to history]' \
        {--overwrite,-o}'[overwrite if the file already has lyrics]' \
        {--dry-run,-t}'[test, only print lyrics, dont write to tags]' \
        '--help[show this]' \
        '--rm-explicit[remove the "Explicit" lyrics warning from the title tag]' \
        {--site,-s}'[specify lyrics site]':lyrics-site:_lyrics-site
}
_nicole "$@"
