# Skill: generate-tests

## Цель

Автоматически генерирует юнит-тесты для указанных функций или модулей.
Определяет язык проекта и использует соответствующий фреймворк:
- **Python** → pytest
- **JavaScript / TypeScript** → Jest

## Как вызвать

```
/generate-tests [путь к файлу или функции]
```

Примеры:
```
/generate-tests src/utils/parser.py
/generate-tests src/auth/login.js::validateToken
```

## Входные данные

| Параметр | Обязателен | Описание |
|----------|-----------|----------|
| `target` | Да | Путь к файлу или `файл::функция` |
| `--only FUNC` | Нет | Генерировать тесты только для одной функции |
| `--cover-edge` | Нет | Включить граничные и негативные кейсы |

## Алгоритм выполнения

1. Прочитать указанный файл и извлечь публичные функции/методы.
2. Для каждой функции определить:
   - сигнатуру (аргументы, типы, возвращаемое значение),
   - happy-path сценарии,
   - граничные случаи (пустые значения, `None`/`undefined`, большие числа),
   - ожидаемые исключения.
3. Определить язык по расширению файла (`.py` → pytest, `.js`/`.ts` → Jest).
4. Сгенерировать тест-файл рядом с исходником:
   - Python: `tests/test_<module>.py`
   - JS/TS: `<module>.test.js` или `__tests__/<module>.test.ts`
5. Вывести список покрытых кейсов и запустить тесты для проверки.

## Выходной формат

```
## Сгенерированные тесты: src/utils/parser.py
Файл: tests/test_parser.py

### Покрытые кейсы
- parse_json: корректный JSON ✓
- parse_json: пустая строка → ValueError ✓
- parse_json: None → TypeError ✓
- parse_url: полный URL ✓
- parse_url: URL без схемы ✓

### Запуск
$ pytest tests/test_parser.py -v
... (вывод pytest)
```

## Шаблоны

### Python (pytest)

```python
import pytest
from <module> import <function>


class Test<FunctionName>:
    def test_<scenario>(self):
        # arrange
        ...
        # act
        result = <function>(...)
        # assert
        assert result == expected

    def test_<scenario>_raises(self):
        with pytest.raises(<ExceptionType>):
            <function>(invalid_input)
```

### JavaScript (Jest)

```js
import { <function> } from './<module>';

describe('<function>', () => {
  it('<scenario>', () => {
    // arrange
    const input = ...;
    // act
    const result = <function>(input);
    // assert
    expect(result).toBe(expected);
  });

  it('throws on invalid input', () => {
    expect(() => <function>(null)).toThrow();
  });
});
```

## Правила качества

- Каждый тест проверяет ровно одно поведение.
- Имена тестов читаются как документация: `test_returns_empty_list_when_input_is_none`.
- Не мокировать то, что не нужно мокировать.
- Если функция имеет внешние зависимости (БД, HTTP) — мокировать их минимально.
