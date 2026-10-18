"""Baut die zu testende Seite: Skelett wie beim Veröffentlichen + Testattrappe vor dem App-Skript."""
import re, sys
src = open('/home/user/Urlaubsplaner/app/urlaubs-team.html', encoding='utf-8').read()
fake = open('/home/user/Urlaubsplaner/qa/harness/fake_claude.js', encoding='utf-8').read()
skeleton = '<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light;padding-block:env(safe-area-inset-top,0px) env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style><script>' + fake + '</script></head><body>'
open('/home/user/Urlaubsplaner/qa/harness/page.html', 'w', encoding='utf-8').write(skeleton + src + '</body></html>')
print('page.html gebaut', len(src))
