import os
import random
import heapq
#from abc import ABC, abstractmethod
#from collections import deque

# Configuración global
OBSTACULOS = [1, 2]  # tipos de obstáculo aleatorio permitidos
MAX_LIM = 30
MIN_LIM = 1

# Utilidades
def preguntar(texto, minimo, maximo):
    while True:
        entrada = input(texto)
        try:
            num = int(entrada)
        except ValueError:
            print("Número inválido. Introduce un entero.")
            continue
        if num < minimo or num > maximo:
            print(f"Número inválido. Debe estar entre {minimo} y {maximo}.")
            continue
        return num

def limpiar():
    os.system('cls' if os.name == 'nt' else 'clear')

# Creamos una clase celda
class Celda:
    def __init__(self, fila, col, tipo = 0):
        self._fila = fila
        self._col = col
        self._tipo = tipo  # 0 libre, 1/2 obstáculo, 3 obstáculo temporal
        self._padre = None
        
        # para el algoritmo de busqueda A*
        self._g = float('inf')
        self._h = 0
        self._f = float('inf')

    @property #convierte el método coordenada en un atributo de solo lectura.
    def coordenada(self):
        return (self._fila, self._col)

    @property #convierte el método tipo en un atributo de solo lectura.
    def tipo(self):
        return self._tipo

    def es_obstaculo(self):
        return self._tipo != 0

    def set_obstaculo(self, tipo = 1):
        self._tipo = tipo

    def quitar_obstaculo(self):
        self._tipo = 0

    def resetar_obstaculo(self):
        self._padre = None
        self._g = float('inf')
        self._h = 0
        self._f = float('inf')

class Mapa:
    def __init__(self, filas, columnas):
        self._filas = filas
        self._columnas = columnas
        
        self._matriz = []
        for i in range(filas):
            fila = []
            for j in range(columnas):
                fila.append(Celda(i, j))
            self._matriz.append(fila)

    @property
    def filas(self):
        return self._filas

    @property
    def columnas(self):
        return self._columnas

    def dentro_de_limites(self, coord):
        f, c = coord
        return 0 <= f < self._filas and 0 <= c < self._columnas

    def obtener_celda(self, coord):
        f, c = coord
        return self._matriz[f][c]

    def es_accesible(self, coord):
        if not self.dentro_de_limites(coord):
            return False
        return not self.obtener_celda(coord).es_obstaculo()

    def obtener_vecinos(self, coord):
        # devuelve lista de coordenadas accesibles (no obstáculo) - 4 direcciones
        f, c = coord
        direcciones = [(-1,0),(1,0),(0,-1),(0,1)]
        vecinos = []
        for df, dc in direcciones:
            nf, nc = f + df, c + dc
            if self.dentro_de_limites((nf, nc)):
                tipo = self.obtener_celda((nf, nc)).tipo
                if tipo != 1 and tipo != 3:
                    vecinos.append((nf, nc))
        return vecinos

    def colocar_obstaculos_aleatorios(self, cantidad):
        filas, columnas = self._filas, self._columnas
        colocados = 0
        #intentos = 0
        #max_intentos = cantidad * 10 + filas * columnas
        while colocados < cantidad: #and intentos < max_intentos:
            fila = random.randrange(0, filas)
            col = random.randrange(0, columnas)
            if self._matriz[fila][col].tipo == 0:
                self._matriz[fila][col].set_obstaculo(random.choice(OBSTACULOS))
                colocados += 1
            #intentos += 1
        if colocados < cantidad:
            print(f"Advertencia: sólo se pudieron colocar {colocados}/{cantidad} obstáculos.")

    def agregar_obstaculo(self, coord, tipo = 3):
        if not self.dentro_de_limites(coord):
            raise ValueError("Coordenada fuera de límites")
        cel = self.obtener_celda(coord)
        cel.set_obstaculo(tipo)

    def quitar_obstaculo(self, coord):
        if not self.dentro_de_limites(coord):
            raise ValueError("Coordenada fuera de límites")
        self.obtener_celda(coord).quitar_obstaculo()
    
    def resetar_obstaculos(self):
        for fila in self._matriz:
            for celda in fila:
                celda.resetar_obstaculo()

    def mostrar(self, opciones = None):
        if opciones is None:
            opciones = {}
        inicio = opciones.get('inicio')
        fin = opciones.get('fin')
        ruta = opciones.get('ruta') or []

        for i in range(self._filas):
            fila_visual = []
            for j in range(self._columnas):
                # prioridad: inicio/fin/ruta antes que valor
                if inicio and (i,j) == inicio:
                    fila_visual.append('🚩')
                    continue
                if fin and (i,j) == fin:
                    fila_visual.append('🏁')
                    continue
                if ruta and any(f == i and c == j for (f, c) in ruta):
                    fila_visual.append('🟩')
                    continue
                val = self._matriz[i][j].tipo
                if val == 0:
                    fila_visual.append('⬜')
                elif val == 1:
                    fila_visual.append('🏢')
                elif val == 2:
                    fila_visual.append('💧')
                elif val == 3:
                    fila_visual.append('⛔')
                else:
                    fila_visual.append('?')
            print(' '.join(fila_visual))

class Ruta:
    def __init__(self, camino):
        # camino: lista de (fila,col) desde inicio a fin
        self.camino = camino or []

    def es_valida(self):
        return bool(self.camino)

    def longitud(self):
        return len(self.camino)


# Algoritmo de Búsqueda (abstracto) y A*
#class AlgoritmoBusqueda(ABC):
#    @abstractmethod
#    def encontrar_ruta(self, mapa, inicio, fin):
#        pass

def heuristica_manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

class AEstrella:
    def __init__(self):
        pass

    def encontrar_ruta(self, mapa, inicio, fin):
        if not mapa.dentro_de_limites(inicio) or not mapa.dentro_de_limites(fin):
            return None
        if mapa.obtener_celda(inicio).es_obstaculo() or mapa.obtener_celda(fin).es_obstaculo():
            return None

        mapa.resetar_obstaculos()

        # heap: (f, contador, (fila,col)) heap es una estructura de datos que funciona como una cola de prioridad
        abrir_heap = []
        contador = 0

        inicio_celda = mapa.obtener_celda(inicio)
        #fin_celda = mapa.obtener_celda(fin)

        inicio_celda._g = 0
        inicio_celda._h = heuristica_manhattan(inicio, fin)
        inicio_celda._f = inicio_celda._g + inicio_celda._h

        heapq.heappush(abrir_heap, (inicio_celda._f, contador, inicio))
        contador += 1

        pasados = set()

        while abrir_heap:
            _, _, actual_coord = heapq.heappop(abrir_heap)
            actual = mapa.obtener_celda(actual_coord)

            if actual_coord == fin:
                # reconstruir ruta
                ruta = []
                nodo = actual
                while nodo is not None:
                    ruta.append(nodo.coordenada)
                    nodo = nodo._padre
                ruta.reverse()
                return Ruta(ruta)

            pasados.add(actual_coord)

            for vecino_coord in mapa.obtener_vecinos(actual_coord):
                if vecino_coord in pasados:
                    continue
                vecino = mapa.obtener_celda(vecino_coord)
                
                # Asignar coste según el tipo de celda
                if vecino.tipo == 0:      # libre
                    coste = 1
                elif vecino.tipo == 2:    # agua
                    coste = 2
                elif vecino.tipo == 1:    # edificio
                    coste = 9999 
                else:
                    coste = 1  # por defecto

                estimado_de_g = actual._g + coste # coste uniforme entre celdas

                if estimado_de_g < vecino._g:
                    vecino._padre = actual
                    vecino._g = estimado_de_g
                    vecino._h = heuristica_manhattan(vecino_coord, fin)
                    vecino._f = vecino._g + vecino._h
                    # añadir al heap (no importa si ya estaba; la versión con peor f quedará ignorada al extraer)
                    heapq.heappush(abrir_heap, (vecino._f, contador, vecino_coord))
                    contador += 1
        # sin ruta
        return None

# Orquestador: CalculadoraDeRutas
class CalculadoraDeRutas:
    def __init__(self):
        self._algoritmo = None
        self._ultima_ruta = None

    def establecer_algoritmo(self, algoritmo):
        self._algoritmo = algoritmo

    def ejecutar_busqueda(self, mapa, inicio, fin):
        if self._algoritmo is None:
            raise RuntimeError("No se estableció algoritmo de búsqueda.")
        self._ultima_ruta = self._algoritmo.encontrar_ruta(mapa, inicio, fin)
        return self._ultima_ruta

    def obtener_ultima_ruta(self):
        return self._ultima_ruta

# Funciones de interacción específicas adaptadas
def pedir_coordenada(texto, mapa):
    filas = mapa.filas
    columnas = mapa.columnas
    while True:
        fila = preguntar(f"Ingresa fila del {texto} (0-{filas-1}): ", 0, filas-1)
        col = preguntar(f"Ingresa columna del {texto} (0-{columnas-1}): ", 0, columnas-1)
        if not mapa.es_accesible((fila, col)):
            print("Esa posición está ocupada por un obstáculo. Intenta otra.")
            continue
        return (fila, col)

def pedir_coordenada_obstaculo(mapa, inicio, fin):
    filas = mapa.filas
    columnas = mapa.columnas
    while True:
        fila = preguntar(f"Ingresa la fila del obstáculo (0-{filas-1}): ", 0, filas-1)
        col = preguntar(f"Ingresa la columna del obstáculo (0-{columnas-1}): ", 0, columnas-1)
        if (fila, col) == inicio or (fila, col) == fin:
            print("No se puede colocar aquí, es inicio/fin. Intenta otra.\n")
            continue
        if not mapa.dentro_de_limites((fila, col)):
            print("Fuera de límites.")
            continue
        if mapa.obtener_celda((fila, col)).es_obstaculo():
            print("Ya hay un obstáculo en esa posición. Intenta otra.\n")
            continue
        return (fila, col)

def pedir_coordenada_quitar_obstaculo(mapa, inicio, fin):
    filas = mapa.filas
    columnas = mapa.columnas
    while True:
        fila = preguntar(f"Ingresa la fila del obstáculo a quitar (0-{filas-1}): ", 0, filas-1)
        col = preguntar(f"Ingresa la columna del obstáculo a quitar (0-{columnas-1}): ", 0, columnas-1)
        if (fila, col) == inicio or (fila, col) == fin:
            print("No puedes quitar el inicio o el fin. Intenta otra coordenada.\n")
            continue
        if not mapa.dentro_de_limites((fila, col)):
            print("Fuera de límites.")
            continue
        if not mapa.obtener_celda((fila, col)).es_obstaculo():
            print("No hay obstáculo en esa posición. Intenta otra coordenada.\n")
            continue
        return (fila, col)
    
def agregar_obstaculo_temporal_interactivo(mapa, ruta, inicio, fin, calc):
    fila, col = pedir_coordenada_obstaculo(mapa, inicio, fin)
    mapa.agregar_obstaculo((fila, col), tipo = 3)  # obstáculo temporal
    # Si obstáculo afecta la ruta actual, recalculamos
    # SIEMPRE recalcula la ruta después de agregar un obstáculo
    nueva_ruta = calc.ejecutar_busqueda(mapa, inicio, fin)
    if nueva_ruta is None:
        limpiar()
        print("La ruta fue bloqueada. No hay camino posible.")
        mapa.mostrar({'inicio': inicio, 'fin': fin})
        ruta = None
    else:
        ruta = nueva_ruta
        limpiar()
        print("¡Ruta encontrada!")
        mapa.mostrar({'inicio': inicio, 'fin': fin, 'ruta': ruta.camino})
    return ruta

def quitar_obstaculo_interactivo(mapa, inicio, fin, calc, ruta_actual):
    fila, col = pedir_coordenada_quitar_obstaculo(mapa, inicio, fin)
    celda = mapa.obtener_celda((fila, col))
    celda._tipo = 0
    celda.resetar_obstaculo()  # <-- Limpia los valores internos
    print("Obstáculo quitado.")
    # Si el obstáculo estaba en la ruta, recalcular
    # SIEMPRE recalcula la ruta después de quitar un obstáculo
    nueva_ruta = calc.ejecutar_busqueda(mapa, inicio, fin)
    if nueva_ruta is None:
        limpiar()
        print("La ruta sigue bloqueada. No hay camino posible.")
        mapa.mostrar({'inicio': inicio, 'fin': fin})
        ruta_actual = None
    else:
        ruta_actual = nueva_ruta
        limpiar()
        print("¡Ruta encontrada!")
        mapa.mostrar({'inicio': inicio, 'fin': fin, 'ruta': ruta_actual.camino})
    return ruta_actual

def agregar_o_quitar_obstaculo_interactivo(mapa, inicio, fin, calc, ruta_actual):
    while True:
        print("\nOpciones:")
        print("1 = Agregar obstáculo")
        print("2 = Quitar obstáculo")
        print("3 = Salir")
        opcion = preguntar("Elige una opción: ", 1, 3)
        if opcion == 3:
            break
        if opcion == 1:
            ruta_actual = agregar_obstaculo_temporal_interactivo(mapa, ruta_actual, inicio, fin, calc)
        elif opcion == 2:
            ruta_actual = quitar_obstaculo_interactivo(mapa, inicio, fin, calc, ruta_actual)

        # Intentar buscar la ruta después de cada cambio
        ruta_actual = calc.ejecutar_busqueda(mapa, inicio, fin)
        if ruta_actual is not None:
            limpiar()
            print("¡Ruta encontrada!")
            mapa.mostrar({'inicio': inicio, 'fin': fin, 'ruta': ruta_actual.camino})
        else:
            limpiar()
            print("La ruta sigue bloqueada. No hay camino posible.")
            mapa.mostrar({'inicio': inicio, 'fin': fin})
            
# Programa principal (CLI)
def main():
    limpiar()
    print("=== Calculadora de Rutas (OOP) ===\n")

    F = preguntar(f"Ingresa número de filas ({MIN_LIM}-{MAX_LIM}): ", MIN_LIM, MAX_LIM)
    C = preguntar(f"Ingresa número de columnas ({MIN_LIM}-{MAX_LIM}): ", MIN_LIM, MAX_LIM)

    mapa = Mapa(F, C)

    max_obstaculos = max(1, F * C - 5)
    cantidad_obstaculos = preguntar(f"Ingresa la cantidad de obstáculos (1-{max_obstaculos}): ", 1, max_obstaculos)

    mapa.colocar_obstaculos_aleatorios(cantidad_obstaculos)

    limpiar()
    print("Mapa inicial:")
    mapa.mostrar()
    print("\n")

    inicio = pedir_coordenada("inicio", mapa)
    print("\n")
    fin = pedir_coordenada("fin", mapa)
    print("\n")
    print("Inicio:", inicio)
    print("Fin:", fin)
    mapa.mostrar({'inicio': inicio, 'fin': fin})
    print("\nBuscando ruta con A*...")

    calc = CalculadoraDeRutas()
    calc.establecer_algoritmo(AEstrella())
    ruta = calc.ejecutar_busqueda(mapa, inicio, fin)

    while ruta is None:
        limpiar()
        print("No se puede encontrar ninguna ruta entre inicio y fin.")
        mapa.mostrar({'inicio': inicio, 'fin': fin})
        print()
        agregar_o_quitar_obstaculo_interactivo(mapa, inicio, fin, calc, ruta)
        ruta = calc.ejecutar_busqueda(mapa, inicio, fin)
        if ruta is not None:
            limpiar()
            print("¡Ruta encontrada!")
            mapa.mostrar({'inicio': inicio, 'fin': fin, 'ruta': ruta.camino})
            
    # Permitir agregar obstáculos temporales interactivamente
    #ruta = agregar_obstaculo_temporal_interactivo(mapa, ruta, inicio, fin, calc)

    limpiar()
    print("¡Ruta encontrada!")
    mapa.mostrar({'inicio': inicio, 'fin': fin, 'ruta': ruta.camino})
    #opción para agregar o quitar obstáculos
    agregar_o_quitar_obstaculo_interactivo(mapa, inicio, fin, calc, ruta)

    print("\nPrograma finalizado. Gracias por usar la calculadora de rutas.")

if __name__ == "__main__":
    main()
