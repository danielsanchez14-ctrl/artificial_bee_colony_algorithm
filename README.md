# Algoritmo Artificial Bee Colony (ABC)

Este repositorio contiene una implementación didáctica del algoritmo de optimización heurística **Artificial Bee Colony (ABC)** en un cuaderno de Jupyter. El algoritmo busca minimizar una función objetivo dentro de los límites definidos para cada variable.

## ¿Qué hace?

La implementación modela las fases principales del algoritmo:

- **Abejas obreras:** generan y evalúan soluciones vecinas.
- **Abejas observadoras:** eligen soluciones según su aptitud y buscan mejorarlas.
- **Abejas exploradoras:** reemplazan soluciones que no han mejorado después del límite de intentos.

El cuaderno guarda el historial de las fases para mostrar cómo evolucionan las soluciones. Incluye un ejemplo que minimiza la suma de cuadrados de cinco variables, acotadas entre `-5.12` y `5.12`.

## Requisitos

- Python 3.9 o posterior.
- JupyterLab e IPython para abrir y ejecutar el cuaderno.
- NumPy y pandas para los cálculos y la presentación de resultados.

## Instalación y ejecución

Desde la raíz del repositorio, crea y activa un entorno virtual. En PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

En macOS o Linux, activa el entorno con:

```bash
source .venv/bin/activate
```

Instala las dependencias y abre JupyterLab:

```bash
python -m pip install jupyterlab ipykernel numpy pandas
jupyter lab
```

En JupyterLab, abre `implementacion.ipynb` y selecciona el kernel de Python del entorno virtual. Ejecuta las celdas en orden (o usa **Run All**) para correr el ejemplo y mostrar la mejor solución, el valor de la función objetivo y el historial de las iteraciones.

## Parámetros del algoritmo

La clase `ArtificialBeeColony` recibe los siguientes parámetros:

- `limit`: intentos sin mejora antes de reiniciar una solución.
- `sn`: número de soluciones o fuentes de alimento.
- `mcn`: número máximo de ciclos.
- `f`: función objetivo, recibida como una función de Python.
- `seed`: semilla para reproducir los resultados aleatorios.

`execute(restrictions)` recibe una lista de pares `(mínimo, máximo)`, uno por dimensión, y devuelve la mejor solución, su valor en la función objetivo y el historial de ejecución.
