---
name: calculations-and-math
description: This skill should be used when performing any mathematical calculation, making numerical claims, computing thresholds, modeling rates or accumulation, comparing quantities, verifying mathematical arguments, or when any agent or meeting participant produces numerical results. Also triggered by "calculate", "how much", "what's the rate", "threshold", "equilibrium", "accumulation", "scales to", "approximately", or any arithmetic, algebra, or statistical claim.
---

# Calculations and Math

All mathematical claims must be backed by computed evidence. No mental math. No approximations without a verified baseline. No hand-waving.

## The Rule

**Every numerical claim must be produced or verified by a computational tool.** This applies to:

- Arithmetic (addition, multiplication, ratios, percentages)
- Algebraic reasoning (solving equations, threshold crossings, equilibrium points)
- Accumulation over time (rates, compound growth, tick-by-tick simulation)
- Statistical claims (distributions, probabilities, expected values)
- Comparisons ("X is greater than Y" where X and Y are computed)
- Parameter validation ("at these settings, the value is Z")
- Unit conversions (KB to MB, pages to bytes, ticks to seconds)

If a number appears in output, a tool produced it. If a claim says "approximately," the exact value was computed first.

## Units Discipline

**Every computed value must carry its unit.** Mixing units without explicit conversion is a bug.

- Label every variable and output with its unit: `free_kb`, `total_mb`, `page_count`
- When converting, show the conversion: `pages * 4096 / 1024 / 1024 = MB`
- When a computation chains through multiple units, verify the final unit matches what's claimed
- Common kernel/systems units: pages (4 KB each), KB, MB, GB, sectors (512 B), jiffies, ticks

**Bad:** `free = 28761088` (free what? pages? bytes? KB?)
**Good:** `free_pages = 28761088  # = 112,348 MB = 109.7 GB`

## How to Compute

Use whichever tool fits the problem. Prefer the simplest tool that handles the job.

### Python 3 (always available)

The universal fallback. Handles arithmetic, string formatting, basic statistics
(stdlib `statistics` module), and multi-step analysis.

```bash
# Quick arithmetic
python3 -c 'print(0.12 * 25)'

# With unit tracking
python3 -c '
pages = 28761088
page_size_kb = 4
mb = pages * page_size_kb / 1024
print(f"{pages:,} pages = {mb:,.1f} MB = {mb/1024:.1f} GB")
'
```

### Python 3 + NumPy/SciPy/SymPy (pip/uv install)

For numerical computing, symbolic math, optimization, and scientific analysis.
Install with `pip install numpy scipy sympy` or `uv pip install numpy scipy sympy`.

```bash
# Symbolic algebra (sympy)
python3 -c '
from sympy import symbols, solve
x = symbols("x")
print(solve(0.12*x - 2.0, x))
'

# Array operations, linear algebra (numpy)
python3 -c '
import numpy as np
orders = np.arange(11)
counts = np.array([3767, 2300, 1327, 802, 453, 326, 73, 24, 9, 0, 28087])
pages = counts * (2**orders)
print(f"Total free: {pages.sum():,} pages = {pages.sum() * 4 / 1024 / 1024:.1f} GB")
'

# Curve fitting, optimization, integration (scipy)
python3 -c '
from scipy import optimize
result = optimize.brentq(lambda x: 0.12*x - 2.0, 0, 100)
print(f"Zero crossing at x = {result:.4f}")
'

# Statistical distributions (scipy.stats)
python3 -c '
from scipy import stats
# 95% confidence interval for mean of 50 samples
ci = stats.t.interval(0.95, df=49, loc=21.5, scale=3.2)
print(f"95% CI: ({ci[0]:.2f}, {ci[1]:.2f})")
'
```

### R (Rscript)

For statistical analysis, data exploration, and publication-quality statistics.

```bash
Rscript -e 'summary(rnorm(1000, mean=3, sd=0.5))'

# Hypothesis testing
Rscript -e '
before <- c(21.5, 18.2, 30.1)
after <- c(7.6, 7.7, 7.5)
t.test(before, after, paired=TRUE)
'
```

### GNU Octave

For numerical computing, matrix operations, and MATLAB-compatible analysis.

```bash
octave --eval "x = linspace(0,1,100); y = x.^2; trapz(x,y)"
```

### Maxima

For exact symbolic computation, computer algebra, and closed-form solutions.

```bash
maxima --batch-string="solve(0.12*x = 2.0, x);"
```

### SageMath (when available)

For advanced algebra, number theory, and combinatorics. Not packaged in Fedora;
install separately if needed.

```bash
sage -c 'var("x"); solve(0.12*x - 2.0, x)'
```

### Multi-step analysis or simulation

Write a temporary script and execute it:

```bash
python3 << 'EOF'
# Simulate fill timing: how long to allocate N GB in 256MB chunks?
chunk_mb = 256
target_mb = 122123
time_per_chunk_s = 0.4  # memset + mbind + MADV_COLD

num_chunks = target_mb / chunk_mb
total_time_s = num_chunks * time_per_chunk_s

print(f"Chunks: {num_chunks:.0f}")
print(f"Estimated fill time: {total_time_s:.0f}s ({total_time_s/60:.1f} min)")
print(f"After 5s wait: {5/time_per_chunk_s:.0f} chunks = {5/time_per_chunk_s * chunk_mb:.0f} MB")
EOF
```

## Tool Selection Guide

| Problem type | First choice | Alternatives |
|---|---|---|
| Arithmetic, unit conversion | `python3 -c` | any |
| Address / bit-shift arithmetic | `python3 -c` (with hex output) | Octave |
| Multi-step / simulation | `python3` script | Octave |
| Symbolic algebra, calculus | SymPy | Maxima, SageMath |
| Numerical arrays, linear algebra | NumPy | Octave |
| Optimization, integration | SciPy | Octave |
| Statistical tests, distributions | R or SciPy | |
| Exact symbolic results | Maxima or SymPy | SageMath |
| Data exploration, plotting | R or NumPy+matplotlib | Octave |

## Intermediate Verification

When a computation chains through multiple steps, verify intermediates. Each
step's output should be checkable independently.

**Bad:**
```python
result = (total_kb * fill_pct / 100 - (total_kb - free_kb)) * 1024
print(f"Need to allocate: {result} bytes")
```

**Good:**
```python
total_kb = 132092416
free_kb = 127695360
fill_pct = 98

target_used_kb = total_kb * fill_pct / 100
current_used_kb = total_kb - free_kb
to_alloc_kb = target_used_kb - current_used_kb
to_alloc_bytes = to_alloc_kb * 1024

print(f"Total: {total_kb/1024:.0f} MB")
print(f"Free: {free_kb/1024:.0f} MB")
print(f"Target used ({fill_pct}%): {target_used_kb/1024:.0f} MB")
print(f"Current used: {current_used_kb/1024:.0f} MB")
print(f"To allocate: {to_alloc_kb/1024:.0f} MB = {to_alloc_bytes/1024/1024/1024:.1f} GB")
```

Each intermediate is labeled, has units, and can be sanity-checked.

## Format for Reporting Results

When presenting computed results, include the computation inline or immediately adjacent:

**Good:**
```
Metabolic floor at max infrastructure: 0.12 * 25 = 3.0 weighted
(python3 -c 'print(0.12 * 25)' -> 3.0)
```

**Good:**
```
Fill at 98% leaves 2,579 MB free on a 128,934 MB node:
(ran: python3 -c 'print(128934 * (100-98) / 100)')
```

**Bad:**
```
Metabolic floor at max infrastructure is approximately 3.0
```
(No computation shown. "Approximately" without a verified baseline.)

**Bad:**
```
The fill leaves about 10 GB free
```
("About" is not a number. Compute it.)

## When Delegating to Agents

When spawning subagents for design meetings, reviews, or analysis that involves numerical reasoning, include this directive in the agent prompt:

> **Math rule:** Every numerical claim must be computed using a tool (python3, R, octave, maxima, or equivalent). No mental math. Show the computation alongside the claim. If a number appears in your output, a tool produced it. Label every value with its unit.

## Address and Bit-Shift Arithmetic

Bit shifts, page frame numbers, masks, and IO virtual addresses are high-risk
for mental math errors. A `<< 12` vs `<< 13` mistake produces a plausible but
wrong address. **Always compute and display in both decimal and hex.**

```bash
# Page frame number to physical address
python3 -c '
pfn = 0x1a3f00
page_shift = 12
phys_addr = pfn << page_shift
print(f"PFN 0x{pfn:x} -> phys 0x{phys_addr:x} ({phys_addr / (1024**3):.2f} GB)")
'

# IOVA calculation with mask
python3 -c '
iova_base = 0xffff_8880_0000_0000
offset = 0x3000
page_mask = ~0xfff & 0xffff_ffff_ffff_ffff
aligned = (iova_base + offset) & page_mask
print(f"IOVA: 0x{iova_base + offset:016x}")
print(f"Page-aligned: 0x{aligned:016x}")
print(f"Offset within page: 0x{(iova_base + offset) & 0xfff:x}")
'

# IOMMU page table index extraction
python3 -c '
addr = 0x0000_7f3c_8a00_0000
# Typical 4-level IOMMU: 9 bits per level, 12-bit page offset
l1 = (addr >> 12) & 0x1ff  # PTE index
l2 = (addr >> 21) & 0x1ff  # PMD index
l3 = (addr >> 30) & 0x1ff  # PUD index
l4 = (addr >> 39) & 0x1ff  # PGD index
print(f"Address: 0x{addr:016x}")
print(f"PGD[{l4}] PUD[{l3}] PMD[{l2}] PTE[{l1}]")
print(f"  = PGD[0x{l4:x}] PUD[0x{l3:x}] PMD[0x{l2:x}] PTE[0x{l1:x}]")
'
```

**Rules for address math:**
- Always show hex alongside decimal for addresses and masks
- When shifting, state the shift amount AND what it represents (PAGE_SHIFT, order, etc.)
- When masking, show the mask value and verify bit width matches the architecture
- For multi-level page table walks, compute and display each level's index separately
- Verify results against known constants: PAGE_SIZE=4096=0x1000, PMD_SIZE=2MB=0x200000, PUD_SIZE=1GB=0x40000000

## Edge Cases

- **Trivial arithmetic** (1+1, 10/2): Still compute it. The cost is one bash call. The benefit is never being wrong about "trivial" math that turns out to matter. The difference between 92% and 98% fill was 7 GB vs 122 GB of allocation — "trivial" percentage math determined whether the reproducer worked.
- **Bit shifts**: Never mentally evaluate `1 << N` for N > 4. Compute it. `1 << 21` is not obviously 2097152 and agents regularly get these wrong.
- **Estimates and ranges**: Compute the bounds. "Between X and Y" requires computing both X and Y.
- **Citing existing computed results**: If a number was already computed earlier in the conversation and is being referenced, cite where it was computed. Do not re-derive mentally.
- **Domain-specific formulas**: When applying a formula from the codebase, read the code to get the exact formula, then compute with the actual parameter values.
- **Buddy allocator math**: Order N = 2^N pages = 2^N * 4 KB. Always compute total free as `sum(count[i] * 2^i)` for all orders, never eyeball it.
- **Percentage thresholds**: When a percentage determines behavior (fill level, watermark, ratio), compute the absolute values at that percentage on the actual system. "92% of 129 GB" and "92% of 16 GB" are very different constraints.
- **Address alignment**: When claiming an address is aligned to N bytes, compute `addr % N` and verify it's zero. Don't eyeball hex digits.
