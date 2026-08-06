"""
ScoutVision Core
Engine Contracts

Every engine in ScoutVision Core must obey these rules.

1. Engines receive Core Models as input whenever possible.

2. Engines return Core Models as output.

3. Engines never return anonymous dictionaries.

4. Engines never generate presentation text.

5. Engines are deterministic.

6. Engines are position-agnostic whenever possible.
"""
