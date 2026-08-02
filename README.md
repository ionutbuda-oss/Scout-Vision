# Scouting Engine V1

## Structură

- `databases/` - bazele originale
- `engine/` - logica aplicației
- `outputs/prepared/` - baze filtrate și curățate
- `outputs/rankings/` - clasamente
- `outputs/charts/` - grafice
- `outputs/reports/` - rapoarte PDF
- `templates/` - șabloane HTML/CSS

## Primul test

1. Copiază `L3-France.xlsx` în `databases/`.
2. Deschide terminalul în acest folder.
3. Rulează:

```bash
python3 main.py
```

Rezultatul corect va afișa:

```text
Project structure is valid.
```

## Instalare biblioteci

```bash
python3 -m pip install -r requirements.txt
```
