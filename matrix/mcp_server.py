"""
Matrix MCP Server — экспорт/импорт данных через Model Context Protocol.

Запуск: python matrix/mcp_server.py
Настройка в .claude/settings.json (секция mcpServers → matrix).
"""
import json
import sys
from pathlib import Path

# Add parent dir so 'matrix' package is importable when run directly
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import mcp.types as types

from matrix import MatrixDB
from exporter import MatrixExporter

DB_PATH = Path(__file__).parent / "matrix.db"

app = Server("matrix-data")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="matrix_summary",
            description="Возвращает сводку матрицы: кол-во записей, выручку, расходы",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="matrix_export_csv",
            description="Экспортирует таблицу матрицы в CSV файл",
            inputSchema={
                "type": "object",
                "properties": {
                    "table":  {"type": "string", "enum": ["clients","projects","tasks","transactions","contacts"]},
                    "output": {"type": "string", "description": "Путь к выходному файлу"},
                },
                "required": ["table", "output"],
            },
        ),
        Tool(
            name="matrix_export_excel",
            description="Экспортирует всю матрицу в Excel (все листы + сводка)",
            inputSchema={
                "type": "object",
                "properties": {
                    "output": {"type": "string", "description": "Путь к .xlsx файлу"},
                },
                "required": ["output"],
            },
        ),
        Tool(
            name="matrix_import_csv",
            description="Импортирует данные из CSV в указанную таблицу",
            inputSchema={
                "type": "object",
                "properties": {
                    "table": {"type": "string", "enum": ["clients","projects","tasks","transactions","contacts"]},
                    "input": {"type": "string", "description": "Путь к CSV файлу"},
                },
                "required": ["table", "input"],
            },
        ),
        Tool(
            name="matrix_export_json",
            description="Экспортирует всю матрицу в один JSON файл",
            inputSchema={
                "type": "object",
                "properties": {
                    "output": {"type": "string", "description": "Путь к .json файлу"},
                },
                "required": ["output"],
            },
        ),
        Tool(
            name="matrix_query",
            description="Выполняет произвольный SELECT-запрос к матрице (только чтение)",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql":    {"type": "string"},
                    "params": {"type": "array", "items": {}, "default": []},
                },
                "required": ["sql"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    with MatrixDB(DB_PATH) as db:
        exp = MatrixExporter(db)

        if name == "matrix_summary":
            result = db.summary()
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

        if name == "matrix_export_csv":
            exp.to_csv(arguments["table"], Path(arguments["output"]))
            return [TextContent(type="text", text=f"✓ CSV экспортирован: {arguments['output']}")]

        if name == "matrix_export_excel":
            exp.to_excel(Path(arguments["output"]))
            return [TextContent(type="text", text=f"✓ Excel экспортирован: {arguments['output']}")]

        if name == "matrix_import_csv":
            count = exp.from_csv(arguments["table"], Path(arguments["input"]))
            return [TextContent(type="text", text=f"✓ Импортировано {count} строк в '{arguments['table']}'")]

        if name == "matrix_export_json":
            exp.to_json(Path(arguments["output"]))
            return [TextContent(type="text", text=f"✓ JSON экспортирован: {arguments['output']}")]

        if name == "matrix_query":
            sql = arguments["sql"].strip()
            if not sql.upper().startswith("SELECT"):
                return [TextContent(type="text", text="❌ Только SELECT-запросы разрешены")]
            rows = db._query(sql, arguments.get("params", []))
            return [TextContent(type="text", text=json.dumps(rows, indent=2, ensure_ascii=False))]

    return [TextContent(type="text", text=f"❌ Неизвестный инструмент: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
