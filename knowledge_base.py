"""
knowledge_base.py
------------------
Curated reference material for the RAG pipeline.

Each entry is a small, self-contained piece of Python knowledge:
a common pattern, a stdlib/library usage example, or a best-practice tip.
These get embedded and stored in a vector database so the agent can
retrieve the most relevant ones for a given user request.

Feel free to add more entries -- more coverage = better retrieval.
"""

KNOWLEDGE_BASE = [
    # ---------- File I/O ----------
    {
        "topic": "file_io",
        "text": (
            "Read a text file line by line using a context manager: "
            "with open('file.txt', 'r') as f:\n    for line in f:\n        print(line.strip())"
        ),
    },
    {
        "topic": "file_io",
        "text": (
            "Write to a file safely using 'with' so it auto-closes: "
            "with open('output.txt', 'w') as f:\n    f.write('hello world')"
        ),
    },
    {
        "topic": "file_io",
        "text": (
            "Read and write JSON files using the json module: "
            "import json\n"
            "with open('data.json') as f:\n    data = json.load(f)\n"
            "with open('out.json', 'w') as f:\n    json.dump(data, f, indent=2)"
        ),
    },

    # ---------- pandas / data processing ----------
    {
        "topic": "pandas",
        "text": (
            "Read a CSV file into a DataFrame with pandas: "
            "import pandas as pd\n"
            "df = pd.read_csv('file.csv')\n"
            "print(df.head())"
        ),
    },
    {
        "topic": "pandas",
        "text": (
            "Filter rows in a pandas DataFrame based on a column condition: "
            "filtered = df[df['column_name'] > 10]"
        ),
    },
    {
        "topic": "pandas",
        "text": (
            "Group by a column and aggregate with pandas: "
            "summary = df.groupby('category')['value'].sum().reset_index()"
        ),
    },
    {
        "topic": "pandas",
        "text": (
            "Handle missing values in a DataFrame: "
            "df = df.dropna()  # remove rows with NaN\n"
            "df['col'] = df['col'].fillna(0)  # fill NaN with a default value"
        ),
    },

    # ---------- requests / APIs ----------
    {
        "topic": "requests",
        "text": (
            "Make a GET request to an API and parse JSON with the requests library: "
            "import requests\n"
            "response = requests.get('https://api.example.com/data')\n"
            "response.raise_for_status()\n"
            "data = response.json()"
        ),
    },
    {
        "topic": "requests",
        "text": (
            "Make a POST request with a JSON body: "
            "import requests\n"
            "payload = {'key': 'value'}\n"
            "response = requests.post('https://api.example.com/submit', json=payload)"
        ),
    },
    {
        "topic": "requests",
        "text": (
            "Add authentication headers to an API request: "
            "headers = {'Authorization': 'Bearer YOUR_TOKEN'}\n"
            "response = requests.get(url, headers=headers)"
        ),
    },

    # ---------- error handling ----------
    {
        "topic": "error_handling",
        "text": (
            "Use try/except/finally to handle exceptions safely: "
            "try:\n    result = 10 / 0\n"
            "except ZeroDivisionError as e:\n    print(f'Error: {e}')\n"
            "finally:\n    print('Done')"
        ),
    },
    {
        "topic": "error_handling",
        "text": (
            "Raise a custom exception with a clear message: "
            "class InvalidInputError(Exception):\n    pass\n\n"
            "def validate(x):\n    if x < 0:\n        raise InvalidInputError('x must be non-negative')"
        ),
    },

    # ---------- loops, comprehensions, functions ----------
    {
        "topic": "core_python",
        "text": (
            "Use a list comprehension to transform a list concisely: "
            "squares = [x**2 for x in range(10) if x % 2 == 0]"
        ),
    },
    {
        "topic": "core_python",
        "text": (
            "Define a function with type hints and a docstring (PEP 8 / PEP 484 style): "
            "def add(a: int, b: int) -> int:\n"
            '    """Return the sum of a and b."""\n'
            "    return a + b"
        ),
    },
    {
        "topic": "core_python",
        "text": (
            "Use a dictionary comprehension to build a lookup table: "
            "lookup = {item['id']: item['name'] for item in items}"
        ),
    },
    {
        "topic": "core_python",
        "text": (
            "Sort a list of dictionaries by a specific key: "
            "sorted_items = sorted(items, key=lambda x: x['price'], reverse=True)"
        ),
    },
    {
        "topic": "core_python",
        "text": (
            "Use *args and **kwargs for flexible function signatures: "
            "def log(*args, **kwargs):\n"
            "    print(args, kwargs)"
        ),
    },

    # ---------- decorators / OOP ----------
    {
        "topic": "advanced_python",
        "text": (
            "Write a simple timing decorator to measure function execution time: "
            "import time\n"
            "from functools import wraps\n\n"
            "def timer(func):\n"
            "    @wraps(func)\n"
            "    def wrapper(*args, **kwargs):\n"
            "        start = time.time()\n"
            "        result = func(*args, **kwargs)\n"
            "        print(f'{func.__name__} took {time.time() - start:.4f}s')\n"
            "        return result\n"
            "    return wrapper"
        ),
    },
    {
        "topic": "advanced_python",
        "text": (
            "Define a basic class with a constructor and a method: "
            "class Rectangle:\n"
            "    def __init__(self, width: float, height: float):\n"
            "        self.width = width\n"
            "        self.height = height\n\n"
            "    def area(self) -> float:\n"
            "        return self.width * self.height"
        ),
    },
    {
        "topic": "advanced_python",
        "text": (
            "Use dataclasses for simple data containers instead of writing boilerplate classes: "
            "from dataclasses import dataclass\n\n"
            "@dataclass\n"
            "class Point:\n"
            "    x: float\n"
            "    y: float"
        ),
    },

    # ---------- web scraping ----------
    {
        "topic": "web_scraping",
        "text": (
            "Parse HTML and extract data using BeautifulSoup: "
            "from bs4 import BeautifulSoup\n"
            "import requests\n\n"
            "html = requests.get(url).text\n"
            "soup = BeautifulSoup(html, 'html.parser')\n"
            "titles = [h.text for h in soup.find_all('h2')]"
        ),
    },

    # ---------- regex ----------
    {
        "topic": "regex",
        "text": (
            "Use the re module to find all matches of a pattern in text: "
            "import re\n"
            "emails = re.findall(r'[\\w.+-]+@[\\w-]+\\.[\\w.-]+', text)"
        ),
    },
    {
        "topic": "regex",
        "text": (
            "Validate a string against a pattern using re.match: "
            "import re\n"
            "if re.match(r'^\\d{3}-\\d{4}$', phone):\n    print('valid format')"
        ),
    },

    # ---------- async ----------
    {
        "topic": "async",
        "text": (
            "Run concurrent async tasks with asyncio.gather: "
            "import asyncio\n\n"
            "async def fetch(i):\n"
            "    await asyncio.sleep(1)\n"
            "    return i * 2\n\n"
            "async def main():\n"
            "    results = await asyncio.gather(*(fetch(i) for i in range(5)))\n"
            "    print(results)\n\n"
            "asyncio.run(main())"
        ),
    },

    # ---------- testing ----------
    {
        "topic": "testing",
        "text": (
            "Write a basic unit test using pytest: "
            "def add(a, b):\n    return a + b\n\n"
            "def test_add():\n    assert add(2, 3) == 5"
        ),
    },

    # ---------- style / PEP8 ----------
    {
        "topic": "style",
        "text": (
            "PEP 8 naming conventions: use snake_case for functions and variables, "
            "PascalCase for classes, and UPPER_SNAKE_CASE for constants. "
            "Keep lines under 79-99 characters and use 4 spaces per indent level."
        ),
    },
]
