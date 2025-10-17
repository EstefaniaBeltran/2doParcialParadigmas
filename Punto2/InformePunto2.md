## Punto 2 - Implementación de una Calculadora Basada en el Paradigma de Agentes

### **Diseño de la Solución: Calculadora Basada en el Paradigma de Agentes**

El diseño de la calculadora se basa en el **paradigma de agentes**, donde cada operación aritmética (suma, resta, multiplicación, división y potencia) es gestionada por un **agente autónomo** e independiente. La arquitectura está compuesta por un **modelo principal (CalcModel)**, un conjunto de **agentes de operación (OpAgent)** y un **agente coordinador de entrada/salida (IOAgent)**.

1. **Modelo general (CalcModel):**
   Es el entorno donde viven y se comunican los agentes. Utiliza un **scheduler** (planificador) que ejecuta los pasos del modelo de manera ordenada, y un **sistema de colas de mensajes** para permitir la comunicación entre agentes. Cada “tick” del modelo representa un ciclo en el que todos los agentes procesan los mensajes que tienen pendientes.

2. **Agentes de operación (OpAgent):**
   Cada uno representa una operación matemática específica:

   * `add_agent` → suma
   * `sub_agent` → resta
   * `mul_agent` → multiplicación
   * `div_agent` → división
   * `pow_agent` → potencia

   Estos agentes funcionan de forma **reactiva**: cuando reciben un mensaje de tipo `"compute"`, realizan la operación con los operandos dados y envían el resultado de vuelta al agente que hizo la solicitud. Si ocurre un error (por ejemplo, división por cero), envían un mensaje de tipo `"error"`.

3. **Agente de entrada/salida (IOAgent):**
   Es el **coordinador principal**. Su tarea es recibir la expresión del usuario (por ejemplo, `2 + 3 * 4`), **analizarla sintácticamente usando el módulo `ast`**, identificar las operaciones y distribuirlas entre los agentes correspondientes.
   El IOAgent:

   * Descompone la expresión en un árbol de operaciones (AST).
   * Crea solicitudes de cálculo (`compute`) a los agentes apropiados.
   * Espera los resultados de cada suboperación.
   * Combina los resultados para obtener el valor final.

4. **Comunicación y coordinación:**
   La comunicación entre agentes se realiza mediante **mensajes almacenados en colas** (`message_queues`), donde cada agente tiene su propia bandeja de entrada. Cuando el IOAgent necesita un resultado, envía un mensaje a un agente de operación, y este le responde cuando termina el cálculo.
   Esta estrategia permite que las operaciones se realicen de forma **paralela y distribuida**, siguiendo el principio de autonomía y colaboración entre agentes.

5. **Gestión de precedencia y recursividad:**
   Gracias al uso del árbol sintáctico (`ast`), el IOAgent respeta automáticamente la **precedencia de operadores** (por ejemplo, multiplicaciones y divisiones antes de sumas y restas). Además, puede manejar expresiones complejas con paréntesis y funciones matemáticas (`sin`, `cos`, `sqrt`, etc.).

6. **Flujo general del sistema:**

   * El usuario ingresa una expresión matemática.
   * El IOAgent analiza la expresión y la descompone en suboperaciones.
   * Se envían mensajes a los agentes correspondientes.
   * Cada OpAgent procesa su operación y devuelve el resultado.
   * El IOAgent recopila los resultados parciales, los combina y devuelve el resultado final.

7. **Ventajas del diseño:**

   * Modularidad: cada agente realiza una tarea específica.
   * Escalabilidad: se pueden agregar más agentes (por ejemplo, para logaritmos o raíces).
   * Simulación realista del comportamiento distribuido y cooperativo.
   * Permite observar el flujo de mensajes y la sincronización paso a paso (ticks).

## Descripción de cómo funciona la comunicación entre agentes durante el cálculo de una expresión.
![Diagrama c1](../Imagenes/c6.png)

 1. `[3]` : Este número entre corchetes indica el **tick**, o sea, el **instante de tiempo dentro de la simulación**.
En MESA, cada “tick” es como un turno donde los agentes actúan.

>  Tick 0 → primer paso de ejecución.
>  Tick 1 → segundo paso, y así sucesivamente.

Así sabes **en qué orden** ocurrieron las operaciones.

 2. `Resultado`: Esto significa que un agente **ha terminado una operación** y envía su resultado a otro agente (o al sistema de entrada/salida).

 3. `c5ee3905-35ce-4e69-bbf4-59c4460f144d` : Ese texto es un **identificador único (UUID)**.

Cada operación matemática que los agentes resuelven (por ejemplo, “3 * 4”) tiene su propio identificador, para que el sistema sepa a qué cálculo pertenece ese resultado.

> Es como un “número de seguimiento” del paquete (la operación).

 4. `= -3646.25 : Este es el **resultado numérico** que el agente calculó.
En este caso, fue una multiplicación (`3 * 4`) y dio `12.0`.

 5. `(from mul_agent)`: Esto indica **quién** hizo el cálculo:

* `mul_agent` → agente de multiplicación.
* `add_agent` → agente de suma.
* `sub_agent` → agente de resta.
* `div_agent` → agente de división.
* `pow_agent` → agente de potencia.

Entonces aquí se está diciendo:

>  “En el tick 3, el **agente de multiplicación** terminó una operación cuyo resultado fue **-3646.25**, y la operación estaba identificada con el código `c5ee3905-35ce-4e69-bbf4-59c4460f144d`.”

---

### 💬 En palabras simples

Piensa que la línea es un **mensaje de los agentes contándote lo que hicieron**:

> 🧮 “Yo, el agente de multiplicar, en el paso 0 calculé 3×4 y saqué 12.”

Después otro agente (por ejemplo, el de suma o resta) usa ese 12 para continuar la expresión completa.

---

¿Quieres que te muestre un **dibujo tipo diagrama de flujo** de cómo los agentes se comunican para resolver una expresión como `2 + 3 * 4 - 5`?
Así ves visualmente quién habla con quién y en qué orden ocurre todo 💬🔁


