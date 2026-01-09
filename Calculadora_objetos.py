import os
import random
from collections import deque

# Configuración global
# Tipos de obstáculo:
OBSTACULOS = [1, 2]


def preguntar(texto, minimo, maximo):
    
    #Pide un número entero por consola validando que esté entre minimo y maximo.
    while True:
        entrada = input(texto)
        
        try:
            num = int(entrada)
        
        except ValueError:  # si no se pudo convertir a entero
            print("Número inválido. Introduce un entero.")
            continue
        
        if num < minimo or num > maximo:
            print(f"Número inválido. Debe estar entre {minimo} y {maximo}.")
            continue
        
        return num

def limpiar():
    
    os.system('cls' if os.name == 'nt' else 'clear')


def crear_mapa(filas, columnas):
    
    #Crea una matriz (lista de listas) de tamaño filas x columnas
    
    mapa = []
    for i in range(filas):
        fila = []
        for j in range(columnas):
            fila.append(0)
        mapa.append(fila)
         
    return mapa

def mostrar_mapa(mapa, opciones = None):
    #Muestra el mapa en consola usando emojis para hacer más claro
    
    if opciones is None:
        opciones = {}
        
    inicio = opciones.get('inicio')
    fin = opciones.get('fin')
    ruta = opciones.get('ruta') or []

    filas = len(mapa)
    if filas > 0:
        columnas = len(mapa[0])
    else:
        columnas = 0

    for i in range(filas):
        fila_visual = []
        for j in range(columnas):
            # Prioridad: inicio/fin/ruta antes que el valor del mapa
            if inicio and i == inicio[0] and j == inicio[1]:
                fila_visual.append('🚩')
                continue
            if fin and i == fin[0] and j == fin[1]:
                fila_visual.append('🏁')
                continue
            if ruta and any(r == i and c == j for (r, c) in ruta):
                fila_visual.append('🟩')
                continue

            val = mapa[i][j]
            if val == 0:
                fila_visual.append('⬜')
            elif val == 1:
                fila_visual.append('🏢')
            elif val == 2:
                fila_visual.append('💧')
            elif val == 3:
                fila_visual.append('⛔')
            else:
                fila_visual.append('?')  # por si aparece algo inesperado
        print(' '.join(fila_visual))

def colocar_obstaculos(mapa, cantidad):
    #Coloca 'cantidad' de obstáculos aleatorios en el mapa.
    
    filas = len(mapa)
    columnas = len(mapa[0])
    colocados = 0
    intentos = 0
    #max_intentos = cantidad * 10 + filas * columnas  # límite de seguridad

    while colocados < cantidad: #and intentos < max_intentos:
        fila = random.randrange(0, filas)
        col = random.randrange(0, columnas)
        if mapa[fila][col] == 0:  # solo en celdas libres
            mapa[fila][col] = random.choice(OBSTACULOS)
            colocados += 1
        intentos += 1

    if colocados < cantidad:
        print(f"Advertencia: sólo se pudieron colocar {colocados}/{cantidad} obstáculos.")


# Pedir coordenadas (inicio/fin / obstáculo manual)
def pedir_coordenada(texto, mapa):
    """
    Pide al usuario una coordenada válida para 'texto' (ej: 'inicio', 'fin').
    Asegura que la celda esté libre (valor 0).
    Retorna una tupla (fila, col).
    """
    filas = len(mapa)
    columnas = len(mapa[0])
    while True:
        fila = preguntar(f"Ingresa fila del {texto} (0-{filas-1}): ", 0, filas-1)
        col = preguntar(f"Ingresa columna del {texto} (0-{columnas-1}): ", 0, columnas-1)
        if mapa[fila][col] != 0:
            print("Esa posición está ocupada por un obstáculo. Intenta otra.")
            continue
        return (fila, col)

def pedir_coordenada_obstaculo(mapa, inicio, fin):
    """
    Pide coordenadas para colocar un obstáculo manual/temporal.
    Valida que no coincida con inicio, fin ni con una celda ocupada.
    """
    filas = len(mapa)
    columnas = len(mapa[0])
    while True:
        fila = preguntar(f"Ingresa la fila del obstáculo (0-{filas-1}): ", 0, filas-1)
        col = preguntar(f"Ingresa la columna del obstáculo (0-{columnas-1}): ", 0, columnas-1)
        if (fila == inicio[0] and col == inicio[1]) or (fila == fin[0] and col == fin[1]) or mapa[fila][col] != 0:
            print("No se puede colocar aquí, ya hay un obstáculo o es inicio/fin. Intenta otra.\n")
            continue
        return (fila, col)


# BFS: búsqueda de la ruta más corta (camino en rejilla)
def buscar_ruta(mapa, inicio, fin):
    """
    Busca la ruta más corta (en número de pasos) desde inicio hasta fin
    usando BFS (cola). Retorna una lista de tuplas [(r,c), ...] desde inicio hasta fin,
    o None si no existe ruta.
    """
    filas = len(mapa)
    columnas = len(mapa[0])

    # Estructuras necesarias:
    cola = deque()
    visitados = []
    for i in range(filas):
        fila_visitados = []
        for j in range(columnas):
            fila_visitados.append(False)
        visitados.append(fila_visitados)

    padres = []
    for i in range(filas):
        fila_padres = []
        for j in range(columnas):
            fila_padres.append(None)
        padres.append(fila_padres)  # para reconstruir la ruta

    inicio_f, inicio_c = inicio
    fin_f, fin_c = fin

    cola.append((inicio_f, inicio_c))
    visitados[inicio_f][inicio_c] = True

    # Vecinos: arriba, abajo, izquierda, derecha
    direcciones = [(-1,0),(1,0),(0,-1),(0,1)]

    while cola:
        f, c = cola.popleft()

        # Si llegamos al destino, reconstruimos la ruta usando 'padres'
        if (f, c) == (fin_f, fin_c):
            ruta = []
            actual = (f, c)
            while actual is not None:
                ruta.append(actual)
                actual = padres[actual[0]][actual[1]]
            ruta.reverse()  # de inicio a fin
            return ruta

        # Revisar vecinos válidos
        for df, dc in direcciones:
            nf, nc = f + df, c + dc
            # comprobar límites, no visitado y que la celda sea transitable (valor 0)
            if 0 <= nf < filas and 0 <= nc < columnas and not visitados[nf][nc] and mapa[nf][nc] == 0:
                cola.append((nf, nc))
                visitados[nf][nc] = True
                padres[nf][nc] = (f, c)

    # Si agotamos la cola sin encontrar el fin, no hay ruta
    return None


# Agregar obstáculos temporales (interacción) 
def agregar_obstaculo_temporal(mapa, ruta, inicio, fin):
    """
    Permite al usuario agregar obstáculos (valor 3) uno por uno.
    Si un nuevo obstáculo bloquea la ruta actual, recalcula con buscar_ruta.
    Si ya no existe ruta, muestra el mapa y termina.
    Retorna la ruta actualizada (o None si quedó bloqueada).
    """
    while True:
        opcion = preguntar("¿Deseas agregar otro obstáculo? 1 = Si, 2 = No: ", 1, 2)
        if opcion == 2:
            break

        fila, col = pedir_coordenada_obstaculo(mapa, inicio, fin)
        mapa[fila][col] = 3  # obstáculo temporal marcado con 3

        # Si el obstáculo está dentro de la ruta actual, recalculamos
        if ruta and any(r == fila and c == col for (r, c) in ruta):
            nueva_ruta = buscar_ruta(mapa, inicio, fin)
            if nueva_ruta is None:
                limpiar()
                print("La ruta fue bloqueada. No hay camino posible.")
                mostrar_mapa(mapa, {'inicio': inicio, 'fin': fin})
                ruta = None
                break
            else:
                ruta = nueva_ruta

        limpiar()
        mostrar_mapa(mapa, {'inicio': inicio, 'fin': fin, 'ruta': ruta})

    return ruta


# Función principal (flujo del programa)
def main():
    limpiar()
    # Pedimos filas y columnas (1-30)
    F = preguntar("Ingresa número de filas (1-30): ", 1, 30)
    C = preguntar("Ingresa número de columnas (1-30): ", 1, 30)

    # Creamos mapa vacío
    mapa = crear_mapa(F, C)

    # Preguntamos cuántos obstáculos aleatorios colocar
    # max_obstaculos = F*C - 5 (dejamos un margen de celdas libres)
    max_obstaculos = max(1, F * C - 5)
    cantidad_obstaculos = preguntar(f"Ingresa la cantidad de obstáculos (1-{max_obstaculos}): ", 1, max_obstaculos)

    # Colocamos obstáculos aleatorios y mostramos el mapa
    colocar_obstaculos(mapa, cantidad_obstaculos)
    mostrar_mapa(mapa, {})
    print("\n")

    # Pedimos coordenadas de inicio y fin (deben ser celdas libres)
    inicio = pedir_coordenada("inicio", mapa)
    print("\n")
    fin = pedir_coordenada("fin", mapa)
    print("\n")

    print("Inicio:", inicio)
    print("Fin:", fin)
    print("\nBuscando ruta...")

    # Buscamos la ruta inicial
    ruta = buscar_ruta(mapa, inicio, fin)
    if ruta is None:
        print("No se puede encontrar ninguna ruta entre inicio y fin.")
        print("Programa finalizado.")
        mostrar_mapa(mapa, {'inicio': inicio, 'fin': fin, 'ruta': ruta})
        return

    # Si encontramos ruta, la mostramos
    limpiar()
    mostrar_mapa(mapa, {'inicio': inicio, 'fin': fin, 'ruta': ruta})

    # Permitimos agregar obstáculos temporales que puedan bloquear la ruta
    ruta = agregar_obstaculo_temporal(mapa, ruta, inicio, fin)

    print("\nPrograma finalizado. Gracias por usar la calculadora de rutas.")

# Al ejecutar el script
if __name__ == "__main__":
    main()
