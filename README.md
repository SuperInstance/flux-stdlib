# FLUX Standard Library

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
Pre-compiled FLUX bytecode programs you can link into your agent.

## Programs (13)

| Program | Category | Input | Output | Description |
|---------|----------|-------|--------|-------------|
| abs | math | R0 | R0 | Absolute value |
| max | math | R0,R1 | R2 | Maximum of two values |
| min | math | R0,R1 | R2 | Minimum of two values |
| factorial | math | R0 | R1 | R0! (handles 0!=1) |
| power | math | R0,R1 | R2 | R0^R1 |
| fibonacci | math | R0,R1,R2 | R1 | Fibonacci sequence |
| gcd | math | R0,R1 | R0 | GCD (Euclidean) |
| sum_to_n | math | R0 | R1 | Sum 1..R0 |
| swap | utility | R0,R1 | R0,R1 | Swap via stack |
| copy | utility | R0 | R1 | Copy register |
| negate | utility | R0 | R0 | Negate value |
| double | utility | R0 | R0 | Double value |
| square | utility | R0 | R1 | Square value |

## Usage

```python
from stdlib import PROGRAMS
result = PROGRAMS["factorial"].run({0: 6})
print(result[1])  # 720
```

16 tests passing.
