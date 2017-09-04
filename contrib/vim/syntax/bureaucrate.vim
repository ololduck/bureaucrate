" bureaucrate syntax file
" Language: bureaucrate DSL
" Maintainer: Paul Ollivier

if exists("b:current_syntax")
    finish
endif

" data types
syn region brcrtString start="'" end="'"

syn region brcrtConfigBlock start="^ *[a-zA-Z]+ {" end="^ *}$" contains=brcrtRulesKeywords,brcrtConditionAction,brcrtConditionActionArg

" Rules
syn match brcrtConditionActionArg "'?.+'?" skipwhite contained containedin=brcrtConfigBlock
syn match brcrtConditionAction '[a-z_]+' nextgroup=conditionActionArg skipwhite contained containedin=brcrtConfigBlock
syn keyword brcrtRulesKeywords if and then nextgroup=conditionAction skipwhite contained containedin=brcrtConfigBlock

" Configuration lines


" Comments and TODOs
syn keyword brcrtTodo contained TODO FIXME XXX NOTE
syn match brcrtComment "#.*$" contains=celTodo

let b:current_syntax = "bureaucrate"

hi def link brcrtRulesKeywords Conditional
hi def link brcrtConditionAction Function
hi def link brcrtConditionActionArg Constant
"hi def link configKey Identifier
"hi def link configValue Constant
hi def link brcrtComment Comment
hi def link brcrtTodo Todo
