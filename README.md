# README

This contains the metadata for comprehensive benchmarks to analyze potential compiler regressions

## Dependencies

This requires `pycpuinfo` for the diagnostic CPU information.

```bash
pip install py-cpuinfo --user
```

## Basic Use

The diagnostics can then be exported using the [flatbench](/flatbench.py) and [metadata.py](/metadata.py) scripts:

```bash
# this is the directory to where the rust benchmark data is
repository="../rust-lexical"
target="${repository}/lexical-benchmark/target"
python flatbench.py --target "${target}"
python metadata.py --target "${target}"
python plot.py --repository "${repository}"
```

## Results

The data will be output in the [results](/results/) directory with each result in a directory containing the shorthash of the file. For example, for commit `9b7cac6`, the results are stored under `results/9b7cac6`.

An example of the profiling info is below. This contains the mean benchmark, the upper and lower bound, and the confidence, all grouped by the bench groups and the benchmark name. The results are in nanoseconds.

### Raw Benchmarks

```json
{
  "mean": {
    "canada": {
      "parse_canada_core": 1299484.0578760111,
      "parse_canada_lexical": 1174099.1108035871
    },
    "contrived_denormal10": {
      "parse_f64_core": 9.547369661223229,
      "parse_f64_lexical": 9.024892765168747
    }
  },
  "lower": {
    "canada": {
      "parse_canada_core": 1294971.510482425,
      "parse_canada_lexical": 1166243.1561483613
    },
    "contrived_denormal10": {
      "parse_f64_core": 9.526261257980039,
      "parse_f64_lexical": 8.994481446498016
    }
  },
  "upper": {
    "canada": {
      "parse_canada_core": 1304157.4730729826,
      "parse_canada_lexical": 1182712.22545152
    },
    "contrived_denormal10": {
      "parse_f64_core": 9.570402076208493,
      "parse_f64_lexical": 9.055119922622316
    }
  },
  "confidence": {
    "canada": {
      "parse_canada_core": 0.95,
      "parse_canada_lexical": 0.95
    },
    "contrived_denormal10": {
      "parse_f64_core": 0.95,
      "parse_f64_lexical": 0.95
    }
  },
  "std_dev": {
    "canada": {
      "parse_canada_core": 23543.600828805113,
      "parse_canada_lexical": 41980.392749475715
    },
    "contrived_denormal10": {
      "parse_f64_core": 0.1127078393110621,
      "parse_f64_lexical": 0.1549991088288157
    }
  }
}
```

An example of the metadata is:

```json
{
  "commit": "9b7cac6",
  "platform": {
    "processor": "Intel64 Family 6 Model 183 Stepping 1, GenuineIntel",
    "machine": "AMD64",
    "version": "10.0.22631",
    "release": "10",
    "system": "Windows"
  },
  "cpuinfo": {
    "cpuinfo_version": [
      9,
      0,
      0
    ],
    "cpuinfo_version_string": "9.0.0",
    "arch": "X86_64",
    "bits": 64,
    "count": 28,
    "arch_string_raw": "AMD64",
    "vendor_id_raw": "GenuineIntel",
    "brand_raw": "Intel(R) Core(TM) i7-14700K",
    "hz_actual_friendly": "3.4000 GHz",
    "hz_actual": [
      3400000000,
      0
    ],
    "l2_cache_size": 29360128,
    "stepping": 1,
    "model": 183,
    "family": 6,
    "l3_cache_size": 34603008,
    "hz_advertised_friendly": "3.4180 GHz",
    "hz_advertised": [
      3418000000,
      0
    ],
    "flags": [
      "3dnow"
    ],
    "l2_cache_line_size": 2048,
    "l2_cache_associativity": 7
  },
  "rust": {
    "version": "1.81.0 (eeb90cda1 2024-09-04)",
    "binary": " rustc",
    "commit-hash": " eeb90cda1969383f56a2637cbd3037bdf598841c",
    "commit-date": " 2024-09-04",
    "host": " x86_64-pc-windows-msvc",
    "release": " 1.81.0",
    "LLVM version": " 18.1.7"
  }
}
```

### Plots

The plots are each will be in the `plot` subdirectory, for example, under `results/da4728e/plot` for commit `da4728e`. Examples from this benchmark include:

**JSON Simple - Parse Integer**

![json_random - parse int - core,lexical.png](/results/da4728e/plot/json_random%20-%20parse%20int%20-%20core,lexical.png)

**Earth - Parse Float**

![earth - parse float - core,lexical.png](/results/da4728e/plot/earth%20-%20parse%20float%20-%20core,lexical.png)

**JSON Simple - Write Integer**

![json_simple - write int - fmt,itoa,lexical.png](/results/da4728e/plot/json_simple%20-%20write%20int%20-%20fmt,itoa,lexical.png)

**Random Big Integers - Write Float**

![random_big_ints - write float - dtoa,fmt,lexical,ryu.png](/results/da4728e/plot/random_big_ints%20-%20write%20float%20-%20dtoa,fmt,lexical,ryu.png)
