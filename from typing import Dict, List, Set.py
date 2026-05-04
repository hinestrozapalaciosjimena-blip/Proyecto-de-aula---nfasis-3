from typing import Dict, List, Set

class Grafo:
    def __init__(self) -> None:
        self.grafo: Dict[int, List[int]] = {}

    def agregar_vertice(self, vertice: int) -> None:
        if vertice not in self.grafo:
            self.grafo[vertice] = []

    def agregar_arista(self, vertice1: int, vertice2: int) -> None:
        if vertice1 in self.grafo and vertice2 in self.grafo:
            self.grafo[vertice1].append(vertice2)
            self.grafo[vertice2].append(vertice1) # No dirigido

    def mostrar_grafo(self) -> None:
        for vertice, aristas in self.grafo.items():
            print(f"{vertice}: {aristas}")


    def puede_formar_palabra(grafo: Grafo, etiquetas: Dict[int, str], objetivo: str) -> bool:
    # Función auxiliar para realizar DFS desde un nodo dado
        pass
    def dfs(nodo: int, objetivo_idx: int, visitados: Set[int]) -> bool:
        if objetivo_idx == len(objetivo):
            return True
        visitados.add(nodo)
        for vecino in grafo.grafo.get(nodo, []):
            if vecino not in visitados and etiquetas[vecino] == objetivo[objetivo_idx]:
                if dfs(vecino, objetivo_idx + 1, visitados):
                    return True
            visitados.remove(nodo)
            return False

# Intentamos iniciar el DFS desde cualquier nodo que coincida con el primer carácter del objetivo
        for nodo, etiqueta in etiquetas.items():
            if etiqueta == objetivo[0]:
                if dfs(nodo, 1, set()):
                    return True
            return False


# Ejemplo de uso:
grafo = Grafo()
# Agregar vértices y aristas
grafo.agregar_vertice(0)
grafo.agregar_vertice(1)
grafo.agregar_vertice(2)
grafo.agregar_vertice(3)
grafo.agregar_arista(0, 1)
grafo.agregar_arista(1, 2)
grafo.agregar_arista(2, 3)

# Asignar etiquetas a los nodos
etiquetas: Dict[int, str] = {0: 'C', 1: 'A', 2: 'S', 3: 'A'}

# String objetivo
objetivo = "CASA"

# Ejecutar la función
print(puede_formar_palabra(grafo, etiquetas, objetivo)) # Debería retornar True si el camino es posible
[15/11, 6:10 a. m.] Jerónimo: from typing import Dict, List

def eliminar_nodo_famoso(grafo: Dict[int, List[int]]) -> Dict[int, List[int]]:
# Paso 1: Calcular el grado de entrada de cada nodo
grado_entrada = {nodo: 0 for nodo in grafo} # Inicializar grados de entrada en 0 para cada nodo
for vecinos in grafo.values():
for vecino in vecinos:
grado_entrada[vecino] = grado_entrada.get(vecino, 0) + 1

# Paso 2: Encontrar el nodo con el mayor grado de entrada
nodo_famoso = None
max_grado_entrada = -1
for nodo, grado in grado_entrada.items():
if grado > max_grado_entrada:
nodo_famoso = nodo
max_grado_entrada = grado

# Paso 3: Si no hay un nodo famoso (todos tienen grado de entrada 0), devolver el grafo original
if max_grado_entrada == 0:
return grafo

# Paso 4: Eliminar el nodo famoso y todas sus conexiones
# Eliminar el nodo famoso de la lista de adyacencia
if nodo_famoso in grafo:
del grafo[nodo_famoso]

# Eliminar todas las referencias al nodo famoso en los demás nodos
for vecinos in grafo.values():
if nodo_famoso in vecinos:
vecinos.remove(nodo_famoso)

return grafo

# Ejemplo de uso:
grafo = {
0: [1, 2],
1: [2],
2: [3],
3: []
}

nuevo_grafo = eliminar_nodo_famoso(grafo)
print(nuevo_grafo)