# /build-feature — Автоматичний пайплайн розробки фічі

## Використання
```
/build-feature [опис фічі]
```

## Приклад
```
/build-feature Форма збору лідів з полями ім'я/телефон, відправка в Telegram
```

## Що відбувається автоматично

Крок 1 — Архітектура:
> Use the architect subagent to design the file structure and API contracts for: $ARGUMENTS

Крок 2 — Кодування:
> Use the coder subagent to implement the architecture from the previous step. Write all files completely, no placeholders.

Крок 3 — Синтаксична перевірка:
> Run bash: find . -name "*.js" -newer CLAUDE.md | xargs -I{} node --check {} 2>&1; find . -name "*.py" -newer CLAUDE.md | xargs -I{} python -m py_compile {} 2>&1

Крок 4 — Тести:
> Use the tester subagent to write and run tests for all new code from step 2.

Крок 5 — Review:
> Use the reviewer subagent to do a full code review of all changes. Block on any critical issues.

Крок 6 — Якщо reviewer каже NEEDS CHANGES:
> Use the coder subagent to fix all issues from the reviewer report, then re-run reviewer.

Крок 7 — Коміт:
> Run bash: git add . && git commit -m "feat: $ARGUMENTS"

## Результат
Готовий, протестований, зревʼюований код в одній команді.
