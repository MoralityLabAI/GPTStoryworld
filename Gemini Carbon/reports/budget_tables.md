| model | budget | depth | correct / scored | accuracy (Wilson 95%) | mean Brier | excess Brier | cap-truncated | tokens/hop (median, correct) |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| carbon-filtration-ref (algorithmic ceiling) | 0 | 1 | 57 / 64 | 0.891 (0.79-0.95) | 0.0391 | 0.0 | 0 | 16.0 |
| carbon-filtration-ref (algorithmic ceiling) | 0 | 2 | 1 / 64 | 0.016 (0.00-0.08) | 0.7837 | 0.734 | 0 | 8.0 |
| carbon-filtration-ref (algorithmic ceiling) | 0 | 4 | 0 / 64 | 0.000 (0.00-0.06) | 0.25 | 0.1318 | 0 | None |
| carbon-filtration-ref (algorithmic ceiling) | 0 | 8 | 0 / 64 | 0.000 (0.00-0.06) | 0.25 | 0.1589 | 0 | None |
| carbon-filtration-ref (algorithmic ceiling) | 0 | 12 | 5 / 64 | 0.078 (0.03-0.17) | 0.5951 | 0.4518 | 0 | 1.3 |
| carbon-filtration-ref (algorithmic ceiling) | 64 | 1 | 64 / 64 | 1.000 (0.94-1.00) | 0.0391 | 0.0 | 0 | 64.0 |
| carbon-filtration-ref (algorithmic ceiling) | 64 | 2 | 64 / 64 | 1.000 (0.94-1.00) | 0.0497 | 0.0 | 0 | 32.0 |
| carbon-filtration-ref (algorithmic ceiling) | 64 | 4 | 7 / 64 | 0.109 (0.05-0.21) | 0.25 | 0.1318 | 64 | 16.0 |
| carbon-filtration-ref (algorithmic ceiling) | 64 | 8 | 7 / 64 | 0.109 (0.05-0.21) | 0.25 | 0.1589 | 64 | 8.0 |
| carbon-filtration-ref (algorithmic ceiling) | 64 | 12 | 7 / 64 | 0.109 (0.05-0.21) | 0.36 | 0.2167 | 64 | 5.3 |
| carbon-filtration-ref (algorithmic ceiling) | 256 | 1 | 64 / 64 | 1.000 (0.94-1.00) | 0.0391 | 0.0 | 0 | 184.0 |
| carbon-filtration-ref (algorithmic ceiling) | 256 | 2 | 64 / 64 | 1.000 (0.94-1.00) | 0.0497 | 0.0 | 0 | 128.0 |
| carbon-filtration-ref (algorithmic ceiling) | 256 | 4 | 64 / 64 | 1.000 (0.94-1.00) | 0.1182 | 0.0 | 0 | 64.0 |
| carbon-filtration-ref (algorithmic ceiling) | 256 | 8 | 8 / 64 | 0.125 (0.07-0.23) | 0.6104 | 0.5193 | 64 | 32.0 |
| carbon-filtration-ref (algorithmic ceiling) | 256 | 12 | 7 / 64 | 0.109 (0.05-0.21) | 0.36 | 0.2167 | 64 | 21.3 |
| carbon-filtration-ref (algorithmic ceiling) | 512 | 1 | 64 / 64 | 1.000 (0.94-1.00) | 0.0391 | 0.0 | 0 | 184.0 |
| carbon-filtration-ref (algorithmic ceiling) | 512 | 2 | 64 / 64 | 1.000 (0.94-1.00) | 0.0497 | 0.0 | 0 | 196.0 |
| carbon-filtration-ref (algorithmic ceiling) | 512 | 4 | 64 / 64 | 1.000 (0.94-1.00) | 0.1182 | 0.0 | 0 | 125.0 |
| carbon-filtration-ref (algorithmic ceiling) | 512 | 8 | 64 / 64 | 1.000 (0.94-1.00) | 0.0911 | 0.0 | 0 | 64.0 |
| carbon-filtration-ref (algorithmic ceiling) | 512 | 12 | 7 / 64 | 0.109 (0.05-0.21) | 0.36 | 0.2167 | 64 | 42.7 |
| carbon-filtration-ref (algorithmic ceiling) | 1536 | 1 | 64 / 64 | 1.000 (0.94-1.00) | 0.0391 | 0.0 | 0 | 184.0 |
| carbon-filtration-ref (algorithmic ceiling) | 1536 | 2 | 64 / 64 | 1.000 (0.94-1.00) | 0.0497 | 0.0 | 0 | 196.0 |
| carbon-filtration-ref (algorithmic ceiling) | 1536 | 4 | 64 / 64 | 1.000 (0.94-1.00) | 0.1182 | 0.0 | 0 | 125.0 |
| carbon-filtration-ref (algorithmic ceiling) | 1536 | 8 | 64 / 64 | 1.000 (0.94-1.00) | 0.0911 | 0.0 | 0 | 117.5 |
| carbon-filtration-ref (algorithmic ceiling) | 1536 | 12 | 64 / 64 | 1.000 (0.94-1.00) | 0.1433 | 0.0 | 0 | 117.3 |

| model | depth (hops) | smallest budget with accuracy >= 0.80 |
| --- | ---: | ---: |
| carbon-filtration-ref (algorithmic ceiling) | 1 | 0 |
| carbon-filtration-ref (algorithmic ceiling) | 2 | 64 |
| carbon-filtration-ref (algorithmic ceiling) | 4 | 256 |
| carbon-filtration-ref (algorithmic ceiling) | 8 | 512 |
| carbon-filtration-ref (algorithmic ceiling) | 12 | 1536 |
