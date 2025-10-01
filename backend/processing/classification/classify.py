import re

def checkLink(text: str) -> bool:
    """
    Classify the input text to determine if it's likely to be a hyperlink.
    Args:
        text (str): The text to classify
    Returns:
        bool: true/false
    """
    if not text or not isinstance(text, str):
        return "text"
    
    text = text.strip()
    
    url_patterns = [
        # HTTP/HTTPS URLs
        # note to self: we are basically saying that after http(s): the following chars are not allowed:
        # empty space, \, /, $, ?, #
        r'^https?://[^\s/$.?#].[^\s]*$',
        # FTP URLs
        r'^ftp://[^\s/$.?#].[^\s]*$',
        # URLs without protocol but with common TLDs
        r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.([a-zA-Z]{2,})(\/[^\s]*)?$',
        # URLs with www prefix
        r'^www\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.[a-zA-Z]{2,}(\/[^\s]*)?$',
        # Mailto URLs
        r'^mailto:[^\s@]+@[^\s@]+\.[^\s@]+$'
    ]
    
    for pattern in url_patterns:
        if re.match(pattern, text, re.IGNORECASE):
            return True
    
    url_indicators = ['http://', 'https://', 'ftp://', 'www.', 'mailto:']
    
    text_lower = text.lower()
    for indicator in url_indicators:
        if indicator in text_lower:
            return True
    
    return False

def checkDate(text: str) -> bool:
    """
    Check if  input text os liekly to be a date
    Args:
        text (str): The text to check for dates
    Returns:
        bool: true/false
    """
    if not text or not isinstance(text, str):
        return False
    
    text = text.strip()
    
    numerical_patterns = [
        # MM/DD/YYYY, MM-DD-YYYY, MM.DD.YYYY
        r'\b(0?[1-9]|1[0-2])[\/\-\.](0?[1-9]|[12][0-9]|3[01])[\/\-\.](\d{4})\b',
        # DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
        r'\b(0?[1-9]|[12][0-9]|3[01])[\/\-\.](0?[1-9]|1[0-2])[\/\-\.](\d{4})\b',
        # YYYY/MM/DD, YYYY-MM-DD, YYYY.MM.DD
        r'\b(\d{4})[\/\-\.](0?[1-9]|1[0-2])[\/\-\.](0?[1-9]|[12][0-9]|3[01])\b',
        # MM/DD/YY, MM-DD-YY, MM.DD.YY
        r'\b(0?[1-9]|1[0-2])[\/\-\.](0?[1-9]|[12][0-9]|3[01])[\/\-\.](\d{2})\b',
        # DD/MM/YY, DD-MM-YY, DD.MM.YY
        r'\b(0?[1-9]|[12][0-9]|3[01])[\/\-\.](0?[1-9]|1[0-2])[\/\-\.](\d{2})\b',
        # ISO format: YYYY-MM-DD
        r'\b\d{4}-\d{2}-\d{2}\b',
        # Time with date: YYYY-MM-DD HH:MM:SS or similar
        r'\b\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}(:\d{2})?\b'
    ]
    
    months = [
        'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december',
        'jan', 'feb', 'mar', 'apr', 'may', 'jun',
        'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
    ]

    time = ['am', 'pm', 'est', 'pst', 'cst', 'mst', 'gmt', 'utc']

    written_patterns = [
        # Month DD, YYYY or Month DD YYYY
        r'\b(' + '|'.join(months) + r')\s+(0?[1-9]|[12][0-9]|3[01])(st|nd|rd|th)?,?\s+(\d{4})\b',
        # DD Month YYYY
        r'\b(0?[1-9]|[12][0-9]|3[01])\s+(' + '|'.join(months) + r')\s+(\d{4})\b',
        # Month YYYY
        r'\b(' + '|'.join(months) + r')\s+(\d{4})\b',
        # DD Month
        r'\b(0?[1-9]|[12][0-9]|3[01])\s+(' + '|'.join(months) + r')\b',
        r'\b(' + '|'.join(months) + r')\s+(0?[1-9]|[12][0-9]|3[01])(st|nd|rd|th)?\b',
        # Time formats:
        # 12-hour: 1pm, 01:30PM, 12:45 am
        # 24-hour: 15:30, 03:05
        # Optional time zone
        r'\b('
            r'([1-9]|1[0-2])(:[0-5][0-9])?\s*(' + '|'.join(time) + r')'  # 12-hour format with time zone required
            r'|'
            r'([1-9]|1[0-2]):([0-5][0-9])\s*(' + '|'.join(time) + r')?'  # 12-hour format with minutes required
            r'|'
            r'([01]?[0-9]|2[0-3]):([0-5][0-9])\s*(' + '|'.join(time) + r')?'  # 24-hour format
        r')\b'
    ]

    for pattern in numerical_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    for pattern in written_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    date_indicators = [
        'today', 'tomorrow', 'yesterday', 'next week', 'last week',
        'next month', 'last month', 'next year', 'last year',
        'this morning', 'this afternoon', 'this evening', 'tonight'
    ]
    
    text_lower = text.lower()
    for indicator in date_indicators:
        if indicator in text_lower:
            return True
    
    return False

def checkMath(text: str) -> bool:
    """
    Check if input text is likely to be a mathematical expression or equation
    Args:
        text (str): The text to check for mathematical content
    Returns:
        bool: true/false
    """
    if not text or not isinstance(text, str):
        return False
    
    # if checkLink(str):
    #     return False
    
    text = text.strip()
    
    operators = [
        # Basic arithmetic
        '+', '-', '*', '/', '×', '÷', '=', '^', '**', '±', '∓',
        # Comparison operators
        '<', '>', '≤', '≥', '≠', '≈', '≡', '∝', '∼', '≅',
        # Set theory symbols
        '∈', '∉', '⊂', '⊃', '⊆', '⊇', '∩', '∪', '∅', '⊊', '⊋',
        # Mathematical symbols
        '√', '∛', '∜', '∫', '∬', '∭', '∮', '∑', '∏', '∂', '∆', '∇',
        '∞', 'π', 'α', 'β', 'γ', 'δ', 'ε', 'θ', 'λ', 'μ', 'σ', 'φ', 'ψ', 'ω',
        # Logical operators
        '∧', '∨', '¬', '→', '↔', '⊕', '⊗',
        # Other math symbols
        '°', '′', '″', '‰', '%', '∠', '⊥', '∥', '⟂'
    ]
    
    functions = [
        'sin', 'cos', 'tan', 'sec', 'csc', 'cot', 'sinh', 'cosh', 'tanh',
        'arcsin', 'arccos', 'arctan', 'asin', 'acos', 'atan',
        'log', 'ln', 'exp', 'sqrt', 'abs', 'max', 'min', 'floor', 'ceil',
        'factorial', 'gamma', 'beta', 'mod', 'gcd', 'lcm'
    ]
    
    keywords = [
        'vector', 'matrix', 'determinant', 'eigenvalue', 'eigenvector',
        'transpose', 'inverse', 'rank', 'trace', 'norm', 'dot', 'cross',
        'derivative', 'integral', 'limit', 'series', 'sequence', 'convergence',
        'function', 'domain', 'range', 'continuous', 'differentiable',
        'theorem', 'proof', 'lemma', 'corollary', 'axiom',
        'set', 'subset', 'union', 'intersection', 'complement', 'cardinality',
        'probability', 'statistics', 'variance', 'deviation', 'distribution',
        'algebra', 'geometry', 'calculus', 'topology', 'analysis'
    ]
    
    # Mathematical notation patterns
    patterns = [
        # Fractions: 1/2, 3/4, (x+1)/(y-1)
        r'\b\d+\/\d+\b',
        r'\([^)]+\)\/\([^)]+\)',
        # Exponents: x^2, 2^n, e^x
        r'[a-zA-Z0-9]+\^[a-zA-Z0-9]+',
        # Subscripts: x_1, a_i, A_n
        r'[a-zA-Z]+_[a-zA-Z0-9]+',
        # Function notation: f(x), g(t), sin(x)
        r'[a-zA-Z]+\([^)]*\)',
        # Equations with equals: x = 5, y = 2x + 1
        r'[a-zA-Z]+\s*=\s*[^=]+',
        # Parentheses with math: (x+1), (2n-1), (a,b)
        r'\([^)]*[+\-*/^][^)]*\)',
        # Scientific notation: 1.5e-10, 2E+5
        r'\d+\.?\d*[eE][+-]?\d+',
        # Mathematical ranges: [0,1], (-∞,∞), {1,2,3}
        r'[\[\{]\s*[^,\]\}]*,\s*[^,\]\}]*\s*[\]\}]',
        # Summation notation: Σ, ∑_{i=1}^n
        r'[∑Σ].*[=].*\^',
        # Absolute values: |x|, ||v||
        r'\|[^|]+\|',
        # Mathematical sequences: a_n, x_i, f_k
        r'[a-zA-Z]_[a-zA-Z0-9]+',
        # Matrix notation: [1 2; 3 4], [[a,b],[c,d]]
        r'\[\s*\[.*\].*\]',
        # Vector notation: <1,2,3>, (x,y,z)
        r'<[^>]*,.*>',
        # Prime notation: f', g'', x'''
        r"[a-zA-Z]+'+",
        # Degree symbol with numbers: 90°, 45°
        r'\d+°',
        # Percentage in mathematical context: 25%, 0.5%
        r'\d+\.?\d*%'
    ]
    
    text_lower = text.lower()
    
    # Check for mathematical operators/symbols
    for operator in operators:
        if operator in text:
            return True
    
    # Check for mathematical functions
    for func in functions:
        if func in text_lower:
            return True
    
    # Check for mathematical keywords
    for keyword in keywords:
        if keyword in text_lower:
            return True
    
    # Check for mathematical patterns
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    # Additional heuristics for mathematical content
    # High density of numbers and operators
    math_chars = sum(1 for char in text if char in '0123456789+-*/=<>()[]{}^')
    if len(text) > 0 and (math_chars / len(text)) > 0.3:
        return True
    
    # Single variable expressions: x, y, z, n (common math variables)
    single_var_pattern = r'^\s*[a-zA-Z]\s*$'
    if re.match(single_var_pattern, text):
        return True
    
    return False

def checkAddress(text: str) -> bool:
    """
    Check if input text is likely to be a physical address
    Args:
        text (str): The text to check for address content
    Returns:
        bool: true/false
    """
    if not text or not isinstance(text, str):
        return False
    
    text = text.strip()
    
    # Address indicators
    street_types = [
        'street', 'st', 'avenue', 'ave', 'road', 'rd', 'boulevard', 'blvd',
        'lane', 'ln', 'drive', 'dr', 'court', 'ct', 'circle', 'cir',
        'place', 'pl', 'way', 'parkway', 'pkwy', 'highway', 'hwy',
        'trail', 'terrace', 'ter', 'square', 'sq', 'plaza', 'pl'
    ]
    
    directional_indicators = [
        'north', 'south', 'east', 'west', 'northeast', 'northwest',
        'southeast', 'southwest', 'ne', 'nw', 'se', 'sw'
    ]
    
    unit_indicators = [
        'apt', 'apartment', 'unit', 'suite', 'ste', 'floor', 'fl',
        'room', 'rm', 'building', 'bldg', '#'
    ]
    
    country_indicators = [
        'usa', 'united states', 'canada', 'uk', 'united kingdom',
        'australia', 'france', 'germany', 'japan', 'china', 'india'
    ]
    
    patterns = [
        # House number + street name: 123 Main St, 456 Oak Avenue
        r'\b\d+\s+[A-Za-z\s]+\s+(' + '|'.join(street_types) + r')\b',
        # ZIP codes: 12345, 12345-6789
        r'\b\d{5}(-\d{4})?\b',
        # Postal codes: K1A 0A6, SW1A 1AA
        r'\b[A-Z]\d[A-Z]\s*\d[A-Z]\d\b',
        r'\b[A-Z]{1,2}\d[A-Z]?\s*\d[A-Z]{2}\b',
        # PO Box: P.O. Box 123, PO Box 456
        r'\b(p\.?o\.?\s*box|post\s*office\s*box)\s*\d+\b',
        # Unit numbers: Apt 5, Unit 12A, Suite 100
        r'\b(' + '|'.join(unit_indicators) + r')\s*[A-Za-z0-9]+\b',
        # Street numbers with suffixes: 123A Main St, 456-B Oak Ave
        r'\b\d+[A-Za-z]?\s+[A-Za-z\s]+\s+(' + '|'.join(street_types) + r')\b'
    ]
    
    text_lower = text.lower()
    
    for street_type in street_types:
        if re.search(r'\b' + re.escape(street_type) + r'\b', text_lower):
            return True
    
    for direction in directional_indicators:
        if direction in text_lower and any(st in text_lower for st in street_types):
            return True
    
    for unit in unit_indicators:
        if unit in text_lower:
            return True
    
    for country in country_indicators:
        if country in text_lower and len(text) > 20:
            return True
    
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    # Check for comma-separated address components
    if ',' in text and len(text.split(',')) >= 2:
        parts = [part.strip() for part in text.split(',')]
        state_pattern = r'\b[A-Z]{2}\b'
        zip_pattern = r'\b\d{5}(-\d{4})?\b'
        
        for part in parts[-2:]:
            if re.search(state_pattern, part) or re.search(zip_pattern, part):
                return True
    
    # Check for multiple numeric components (house number, ZIP)
    numbers = re.findall(r'\b\d+\b', text)
    if len(numbers) >= 2 and any(st in text_lower for st in street_types):
        return True
    
    return False

# test = '''
# 349 Ferst Dr NW, Atlanta, GA 30332'''
# # test = "Thursday, September 18th"
# print(checkDate(test))
# print(checkMath(test))
# print(checkAddress(test))