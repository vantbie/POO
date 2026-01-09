# 🏗️ Desafio 2: Evolución OOP

Este proyecto representa la **refactorización total** del motor de búsqueda de rutas. Se ha migrado de un enfoque procedural (funciones sueltas) a una arquitectura robusta basada en **Programación Orientada a Objetos (POO)**, mejorando la escalabilidad, la lectura y el mantenimiento del código.

## ⚙️ ¿Qué hace este sistema?

El programa genera un entorno virtual (grilla) con obstáculos aleatorios y permite encontrar la ruta óptima entre un punto `A` y un punto `B`. Su principal característica ahora es su capacidad de **encapsular responsabilidades**: el mapa sabe cómo dibujarse, las celdas conocen sus costos y la calculadora sabe qué algoritmo aplicar.

## 🏗️ Arquitectura y Diseño (El "Cómo")

La solución se estructura en cuatro clases principales que interactúan entre sí bajo el principio de **Responsabilidad Única**:

### 1. Clase `Celda` (La Unidad Atómica)
Ya no usamos simples números enteros (`0`, `1`). Ahora cada casilla es un objeto inteligente que almacena su propio estado:
- **Coordenadas:** Su ubicación `(x, y)` en el espacio.
- **Tipo:** Si es camino libre, edificio o agua.
- **Costos (A*):** Almacena sus valores `G` (costo desde el inicio), `H` (heurística al destino) y `F` (costo total) para el cálculo de rutas.

### 2. Clase `Mapa` (El Entorno)
Encapsula la matriz bidimensional y protege su integridad.
- **Generación:** Crea la grilla e inyecta obstáculos aleatorios.
- **Validación:** Se encarga de verificar si una coordenada es transitable o está fuera de límites.
- **Renderizado:** Contiene la lógica visual para dibujar el estado actual en la consola.

### 3. Patron Strategy: `AlgoritmoBusqueda` y `AEstrella`
Se implementó un diseño flexible utilizando herencia.
- **`AlgoritmoBusqueda`:** Clase base (interfaz) que define el contrato estándar para buscar rutas.
- **`AEstrella (A*)`:** Implementación concreta del algoritmo. Utiliza una **Cola de Prioridad (`heapq`)** y la **Distancia Manhattan** como heurística para encontrar no solo una ruta, sino la más eficiente posible.

### 4. Clase `CalculadoraDeRutas` (El Contexto)
Actúa como el orquestador o "Cliente".
- No está atada a un solo algoritmo. Gracias al polimorfismo, recibe una instancia de una estrategia de búsqueda (como `AEstrella`) y la ejecuta. Esto permite cambiar el algoritmo (por ejemplo, a Dijkstra o BFS) en el futuro sin tocar el código de la calculadora.

## 🧠 Lógica de Refactorización
Durante la transición a OOP, se priorizó:
- **Encapsulamiento:** Las propiedades del mapa no son accesibles directamente desde el script principal; se accede a ellas a través de métodos controlados.
- **Mantenibilidad:** Si se quiere cambiar cómo se ven los obstáculos, solo se edita la clase `Mapa`. Si se quiere mejorar la búsqueda, solo se toca `AEstrella`.
- **Interacción Dinámica:** El ciclo principal (`main`) se mantiene limpio, delegando toda la lógica compleja a los objetos instanciados.

---
**Estado:** Refactorizado y Optimizado ✅
