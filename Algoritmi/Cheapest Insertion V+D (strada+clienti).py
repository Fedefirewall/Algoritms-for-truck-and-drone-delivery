#region
#IMPORTAZIONE LIBRERIE
import re                                    #Libreria per leggere i file dati in input
import networkx as nx                        #Libreria per costruire grafo
from matplotlib import pyplot as plt
import math
from networkx.classes.function import neighbors
from networkx.drawing.layout import rescale_layout 
import numpy as np     
from typing import Any, List
import time
import json
from tqdm import tqdm
from statistics import mean


start = time.time()


#region
class CustomError_noedges(Exception):
    def __init__(self,*args):
        if args:
            self.message = args[0]
        else:
            self.message = None
    
    def __str__(self):
        print("Nessun arco tra questi nodi:"+(self.message))
        if self.message:
            return "Nessun arco tra questi nodi:"+(self.message)
        else:
            return "base has edge error custom"

class Custom_Graph(nx.Graph):
    def custom_remove_edge(self,node1,node2):
        if self.has_edge(node1,node2):
            self.remove_edge(node1,node2)
        elif self.has_edge(node2,node1):
            self.remove_edge(node2,node1)
        else:
            raise CustomError_noedges(str(node1)+" "+str(node2))
        
#classe per salvare i sotto cicli del drone
class Visited_node_drone:
    def __init__(self, index, trip_number):
        self.index = index
        self.trip_number = trip_number

def print_graph_for_debug():
    graph_total = nx.compose(graph_drone, graph_truck)
    edges = graph_total.edges()
    colors = [graph_total[u][v]['color'] for u,v in edges]
    
    #creo i colori dei nodi
    color_map=[]
    for node in graph_total:
    
            if (node == truck_node_index): 
                color_map.append('red')
            elif (node in visited_list_truck_indexes): 
                color_map.append('white')
            else: 
                color_map.append('green') 
    #colori degli archi aggiunti ogni volta vh faccio add edge

    plt.clf()   #clearo il grafico precedente
    nx.draw(graph_total,points,font_size=10, node_size=200,with_labels=True, arrowsize=20,edge_color=colors,node_color=color_map)  # create a graph with the tour
    labels = nx.get_edge_attributes(graph_total, 'length') 
    #nx.draw_networkx_edge_labels(graph_total,points, edge_labels=labels)
    
    plt.show()         # display it interactively   

def create_graph(solution):

    graph_truck=graph_truck_clear.copy()
    graph_drone=graph_drone_clear.copy()
    graphs_couple=[]
    i=0
    truck_path=solution[0]
    while i < len(truck_path)-1:
        node1=truck_path[i]
        node2=truck_path[i+1]
        graph_truck.add_edge(node1,node2,length=round(dist_truck[node1][node2],2),color='r')
        i+=1
    node1=truck_path[-1]
    node2=truck_path[0]
    graph_truck.add_edge(node1,node2,length=round(dist_truck[node1][node2],2),color='r')

    p=1
    while p < len(solution):
        drone_path=solution[p]
        drone_color=paths_colors[p]
        if len(drone_path)>1:
            i=0
            while i < len(drone_path)-1:
                node1=drone_path[i]
                node2=drone_path[i+1]
                graph_drone.add_edge(node1,node2,length=round(dist_drone[node1][node2],2),color=drone_color)
                i+=1
            
        p+=1

    graphs_couple.append(graph_truck)
    graphs_couple.append(graph_drone)
    
    return graphs_couple
    # for path in solution:
    #     while len(path)>1:
    #         node1=path.pop(0)
    #         node2=path.pop(0)


def print_graph_for_debugs(solution):

    graphs_couple=create_graph(solution)
    graph_truck=graphs_couple[0]
    graph_drone=graphs_couple[1]
    graph_total = nx.compose(graph_truck,graph_drone)
    edges = graph_total.edges()
    colors = [graph_total[u][v]['color'] for u,v in edges]
    visited_list_truck=solution[0]
    visited_list_drone=[]
    drone_paths=[path for path in solution if solution.index(path)!=0]
    for path in solution:
        if solution.index(path)!=0:
            visited_list_drone+=path
    #creo i colori dei nodi
    color_map=[]
    for node in graph_total:
        if (node == starting_node): 
            color_map.append('#ff8000')
        elif (node in visited_list_truck): 
            color_map.append('#d16e66')
        elif (node in visited_list_drone): 
            index=[i for i, path in enumerate(drone_paths) if node in path]
            color_map.append(paths_colors[index[0]+1])
        else: 
            color_map.append('green') 
    #colori degli archi aggiunti ogni volta vh faccio add edge
    
    figure.canvas.manager.window.wm_geometry("+%d+%d" % (-10, 00))
    plt.clf()   #clearo il grafico precedente
    nx.draw(graph_total,points,font_size=9, node_size=170,with_labels=True, arrowsize=20,edge_color=colors,node_color=color_map)  # create a graph with the tour
    labels = nx.get_edge_attributes(graph_total, 'length') 
    #per stampare le distanze
    #nx.draw_networkx_edge_labels(graph_total,points, edge_labels=labels, font_size=7)
     
    
    plt.show()         # display it interactively 

def compute_visited_list_truck():
    visited_list_truck_indexes_1=[node1 for node1,node2 in graph_truck.edges]
    visited_list_truck_indexes_2=[node2 for node1,node2 in graph_truck.edges]
    visited_list_truck_indexes=visited_list_truck_indexes_1+visited_list_truck_indexes_2
    visited_list_truck_indexes=list(set(visited_list_truck_indexes))
    return visited_list_truck_indexes

def compute_visited_list():
    visited_list_truck_indexes_1=[node1 for node1,node2 in graph_truck.edges]
    visited_list_truck_indexes_2=[node2 for node1,node2 in graph_truck.edges]
    visited_list_truck_indexes_3=[node1 for node1,node2 in graph_drone.edges]
    visited_list_truck_indexes_4=[node2 for node1,node2 in graph_drone.edges]
    visited_list_truck_indexes=visited_list_truck_indexes_1+visited_list_truck_indexes_2+visited_list_truck_indexes_3+visited_list_truck_indexes_4
    visited_list_truck_indexes=list(set(visited_list_truck_indexes))
    return visited_list_truck_indexes
#Ricerca del nodo più vicino 
def nearest_node(neighbors_distance,visited_list_indexes):
    min_value=10000000
    for i in range(1,len(neighbors_distance)):  
        #se la distanza non è zero e il nodo non è nella lista dei visitati
        if(not(i in visited_list_indexes)):
            actual_value=neighbors_distance[i]
            actual_index=i
            if(actual_value<min_value):
                min_value=actual_value
                min_index=actual_index
    return min_index

def find_best_edge(graph, dist, trip_number):
    #per ogni coppia di nodi cercoil nodo con costo minore tale che la
    #somma dei nuovi archi sia minima

    #scorro gli archi
    min_index=0
    cost_min=10000

    for node1,node2,attributes in graph.edges(data=True):

        if ([node1,node2] not in truck_locked_edges and trip_number==-1) \
            or (trip_number!=-1 and (any(x.index == node1 and x.trip_number==trip_number for x in visited_list_drone)) \
            and (any(y.index == node2  and y.trip_number==trip_number for y in visited_list_drone))):


            #scorro i nodi
            for i in range(1,client_number_range):  
                #se il nodo non è nella lista dei visitati
                if(not(i in visited_list_indexes)):
                    #calcolo il costo di questo nodo, 
                    #somma dell'arco tra nodo1 nodoX e somma dell' arco tra nodo2 e nodoX
                    new_edge_cost=(dist[i][node1]) + (dist[i][node2])
                    actual_index=i
                    old_edge_cost=dist[node1][node2]
                    actual_cost=compute_solution_cost(dist)-old_edge_cost+new_edge_cost


                    if(actual_cost<cost_min):
                        cost_min=actual_cost
                        min_index=actual_index
                        node1_best=node1
                        node2_best=node2 

    return min_index,node1_best,node2_best;

def compute_solution_cost(dist):    
    cost=0
    for node1,node2,attributes in graph_truck.edges(data=True):
        cost+=dist[node1][node2]
    return cost

def compute_drone_cost_new(trip_number):
    cost=0
    #nodi visitati in questo viaggio
    # per ogni nodo negli archi del drone
    for node1,node2,attributes in graph_drone.edges(data=True):
        # controllo se entrambi i 2 nodi sono stati visitati in questo ciclo
        if ((any(x.index == node1 and x.trip_number==trip_number for x in visited_list_drone)) and (any(y.index == node2  and y.trip_number==trip_number for y in visited_list_drone))):  
            #se entrambi i nodi non sono visitati dal truck(arco iniziale)
            if not (node1  in visited_list_truck_indexes and node2  in visited_list_truck_indexes):
                cost+=dist_drone[node1][node2]
                #print(node1,node2,dist_drone[node1][node2],cost)
    return cost

def compute_drone_weight(trip_number):
    weight=0
    #per ogni nodo controllo se e stato visitato in questo ciclo
    visited_list_drone_this_trip=[node.index for node in visited_list_drone if node.trip_number==trip_number]
    for node in visited_list_drone_this_trip:
        if node not in visited_list_truck_indexes:
            weight+=weights_dict[node]
    return weight

def revert_this_trip(trip_number):
    global visited_list_drone
    global visited_list_indexes
    edges_remove=graph_drone.edges()
    for node1,node2 in edges_remove:
        # controllo se entrambi i 2 nodi sono stati visitati in questo ciclo
        if ((any(x.index == node1 and x.trip_number==trip_number for x in visited_list_drone)) and (any(y.index == node2  and y.trip_number==trip_number for y in visited_list_drone))):  
            graph_drone.custom_remove_edge(node1,node2)

    visited_list_drone = [node for node in visited_list_drone if node.trip_number!=trip_number]

    visited_list_indexes=compute_visited_list()

def find_best_drone_route(cost_routes):
    #spiegare come vengono calcolati i 2 costi possibli, scelgo quello maggiore
    if len(cost_routes)<2:  
        return cost_routes[0]

    if(cost_routes[0][0]>=cost_routes[1][0]):
        return cost_routes[0]
    else:
        return cost_routes[1]

def drone_Cheapest_trip():
    global visited_list_indexes
    best_trip_score=0
    first_time=1
    global drone_trip_counter
    trip_counter_best=0
    #prendo tutti gli archi disponibili nel percorso del truck e con fitness migliore(client +cost*alpha)
    for node1,node2 in graph_truck.edges:
        if([node1,node2] not in truck_locked_edges):
            graph_drone.add_edge(node1,node2,length=round(dist_drone[node1][node2],2),color='#97E5FF')

            visited_list_drone.append(Visited_node_drone(node1,drone_trip_counter))
            visited_list_drone.append(Visited_node_drone(node2,drone_trip_counter))

            cost=compute_drone_cost_new(drone_trip_counter)
            weight=compute_drone_weight(drone_trip_counter)

            while(cost<=drone_autonomy and weight<=drone_capacity and len(visited_list_indexes)<client_number):
                best_node_index,node1_start,node2_start=find_best_edge(graph_drone,dist_drone,drone_trip_counter)
                #Ora ho trovato il nodo con detour di costo minimo, e i 2 nodi a cui collegarlo
                #quindi lo aggiungo e rimuovo l edge corrispondente SOLO SE NON SUPERO I VINCOLI
                weight=compute_drone_cost_new(drone_trip_counter)+weights_dict[best_node_index]
                new_edge_cost=(dist_drone[best_node_index][node1_start]) + (dist_drone[best_node_index][node2_start])

                visited_list_truck_indexes=compute_visited_list_truck()
                # se i 2 nodi da rimuovere sono quellindi arrivo e partenza(sonole perocorso del truck) il costo dell arco é zero
                if((node1_start in visited_list_truck_indexes and node2_start in visited_list_truck_indexes)==False):
                    old_edge_cost=dist_drone[node1_start][node2_start]
                else:
                    old_edge_cost=0

                cost_temp=compute_drone_cost_new(drone_trip_counter)
                cost=cost_temp-old_edge_cost+new_edge_cost
                if(weight<=drone_capacity and cost<=drone_autonomy):
                    graph_drone.add_edge(best_node_index,node1_start,length=round(dist_drone[best_node_index][node1_start],2),color='#97E5FF')
                    graph_drone.add_edge(best_node_index,node2_start,length=round(dist_drone[best_node_index][node2_start],2),color='#97E5FF')

                    visited_list_indexes=compute_visited_list()
                    visited_list_drone.append(Visited_node_drone(best_node_index,drone_trip_counter))
                    # conto quanti clienti sta servendo il drone in questo viaggio
                    visited_list_drone_this_trip=[node.index for node in visited_list_drone if node.trip_number==drone_trip_counter]
                    sub_clients_counter=len(visited_list_drone_this_trip)
                    #lo rimuovo in ogni caso cosi risolvo il rpoblema dell arco obbligatorio
                    graph_drone.custom_remove_edge(node1_start,node2_start)

                    cost=compute_drone_cost_new(drone_trip_counter)
                    weight=compute_drone_weight(drone_trip_counter)
            #controllo lo score solo se la path ha + di 2 nodi
            visited_list_drone_this_trip=[node.index for node in visited_list_drone if node.trip_number==drone_trip_counter]
            if(len(visited_list_drone_this_trip)>2):
               
                cost=compute_drone_cost_new(drone_trip_counter)
                weight=compute_drone_weight(drone_trip_counter)
                
                trip_score=(len(visited_list_drone_this_trip))+(cost*alpha)+(weight*beta)
            
                #se ho trovato un perocorso migliore me lo salvo
                if trip_score>best_trip_score or first_time:
                    best_trip_score=trip_score
                    node1_start_best=node1
                    node2_start_best=node2
                    trip_counter_best=drone_trip_counter
                    first_time=0

            revert_this_trip(drone_trip_counter)          
            drone_trip_counter+=1

    #se frist time é vero allora nessun nodo soddisfa,ritorno FAlse e non cnfermo nessun percorso de drone
    if(first_time)==False:       
        #ora che ho trovato il migliore lo confermo
        graph_drone.add_edge(node1_start_best,node2_start_best,length=round(dist_drone[node1_start_best][node2_start_best],2),color=paths_colors[drone_cycle_number])
        visited_list_drone.append(Visited_node_drone(node1_start_best,trip_counter_best))
        visited_list_drone.append(Visited_node_drone(node2_start_best,trip_counter_best))
        cost=compute_drone_cost_new(trip_counter_best)
        weight=compute_drone_weight(trip_counter_best)
        #e blocco l arco del truck
        truck_locked_edges.append([node1_start_best,node2_start_best])


        #ripercorro il ciclo best

        while(cost<=drone_autonomy and weight<=drone_capacity and len(visited_list_indexes)<client_number):

            best_node_index,node1_start_best,node2_start_best=find_best_edge(graph_drone,dist_drone,trip_counter_best)
            #Ora ho trovato il nodo con detour di costo minimo, e i 2 nodi a cui collegarlo
            #quindi lo aggiungo e rimuovo l edge corrispondente SOLO SE NON SUPERO I VINCOLI
            weight=compute_drone_weight(trip_counter_best)+weights_dict[best_node_index]
            new_edge_cost=(dist_drone[best_node_index][node1_start_best]) + (dist_drone[best_node_index][node2_start_best])

            visited_list_truck_indexes=compute_visited_list_truck()
            # se i 2 nodi da rimuovere sono quellindi arrivo e partenza(sonole perocorso del truck) il costo dell arco é zero
            if((node1_start_best in visited_list_truck_indexes and node2_start_best in visited_list_truck_indexes)==False):
                old_edge_cost=dist_drone[node1_start_best][node2_start_best]
            else:
                old_edge_cost=0

            cost_temp=compute_drone_cost_new(trip_counter_best)
            cost=cost_temp-old_edge_cost+new_edge_cost

            if(weight<=drone_capacity and cost<=drone_autonomy):
                graph_drone.add_edge(best_node_index,node1_start_best,length=round(dist_drone[best_node_index][node1_start_best],2),color=paths_colors[drone_cycle_number])
                graph_drone.add_edge(best_node_index,node2_start_best,length=round(dist_drone[best_node_index][node2_start_best],2),color=paths_colors[drone_cycle_number])

                visited_list_indexes=compute_visited_list()
                visited_list_drone.append(Visited_node_drone(best_node_index,trip_counter_best))
                # conto quanti clienti sta servendo il drone in questo viaggio
                visited_list_drone_this_trip=[node.index for node in visited_list_drone if node.trip_number==trip_counter_best]
                sub_clients_counter=len(visited_list_drone_this_trip)
                #lo rimuovo in ogni caso cosi risolvo il rpoblema dell arco obbligatorio
                graph_drone.custom_remove_edge(node1_start_best,node2_start_best)
                cost=compute_drone_cost_new(trip_counter_best)    
                weight=compute_drone_weight(trip_counter_best)

                
    
        return node1_start_best,node2_start_best
    else:
        return -1,-1
    

def drone_Cheapest_tripss():
    global visited_list_indexes
    best_trip_score=0
    first_time=1
    global drone_trip_counter
    trip_counter_best=0
    #prendo tutti gli archi disponibili nel percorso del truck e con fitness migliore(client +cost*alpha)
    for node1,node2 in graph_truck.edges:
        if([node1,node2] not in truck_locked_edges):
            graph_drone.add_edge(node1,node2,length=round(dist_drone[node1][node2],2),color='#97E5FF')

            visited_list_drone.append(Visited_node_drone(node1,drone_trip_counter))
            visited_list_drone.append(Visited_node_drone(node2,drone_trip_counter))

            cost=compute_drone_cost_new(drone_trip_counter)
            weight=compute_drone_weight(drone_trip_counter)

            while(cost<=drone_autonomy and weight<=drone_capacity and len(visited_list_indexes)<client_number):
                best_node_index,node1_start,node2_start=find_best_edge(graph_drone,dist_drone,drone_trip_counter)
                #Ora ho trovato il nodo con detour di costo minimo, e i 2 nodi a cui collegarlo
                #quindi lo aggiungo e rimuovo l edge corrispondente SOLO SE NON SUPERO I VINCOLI
                weight=compute_drone_weight(drone_trip_counter)+weights_dict[best_node_index]
                new_edge_cost=(dist_drone[best_node_index][node1_start]) + (dist_drone[best_node_index][node2_start])

                visited_list_truck_indexes=compute_visited_list_truck()
                # se i 2 nodi da rimuovere sono quellindi arrivo e partenza(sonole perocorso del truck) il costo dell arco é zero
                if((node1_start in visited_list_truck_indexes and node2_start in visited_list_truck_indexes)==False):
                    old_edge_cost=dist_drone[node1_start][node2_start]
                else:
                    old_edge_cost=0

                cost_temp=compute_drone_cost_new(drone_trip_counter)
                cost=cost_temp-old_edge_cost+new_edge_cost
                if(weight<=drone_capacity and cost<=drone_autonomy):
                    graph_drone.add_edge(best_node_index,node1_start,length=round(dist_drone[best_node_index][node1_start],2),color='#97E5FF')
                    graph_drone.add_edge(best_node_index,node2_start,length=round(dist_drone[best_node_index][node2_start],2),color='#97E5FF')
                    
                    visited_list_indexes=compute_visited_list()
                    visited_list_drone.append(Visited_node_drone(best_node_index,drone_trip_counter))
                    # conto quanti clienti sta servendo il drone in questo viaggio
                    visited_list_drone_this_trip=[node.index for node in visited_list_drone if node.trip_number==drone_trip_counter]
                    sub_clients_counter=len(visited_list_drone_this_trip)
                    #lo rimuovo in ogni caso cosi risolvo il rpoblema dell arco obbligatorio
                    graph_drone.custom_remove_edge(node1_start,node2_start)
                    cost=compute_drone_cost_new(drone_trip_counter)
                    weight=compute_drone_weight(drone_trip_counter)
            #controllo lo score slo se la path ha + di 2 nodi
            visited_list_drone_this_trip=[node.index for node in visited_list_drone if node.trip_number==drone_trip_counter]
            if(len(visited_list_drone_this_trip)>2):
               
                cost=compute_drone_cost_new(drone_trip_counter)
                weight=compute_drone_weight(drone_trip_counter)
                
                trip_score=(len(visited_list_drone_this_trip))+(cost*alpha)+(weight*beta)
            
                #se ho trovato un perocorso migliore me lo salvo
                if trip_score>best_trip_score or first_time:
                    best_trip_score=trip_score
                    node1_start_best=node1
                    node2_start_best=node2
                    trip_counter_best=drone_trip_counter
                    first_time=0


            revert_this_trip(drone_trip_counter)       

            drone_trip_counter+=1

    #se frist time é vero allora nessun nodo soddisfa,ritorno FAlse e non cnfermo nessun percorso de drone
    if(first_time)==False:       
        #ora che ho trovato il migliore lo confermo
        graph_drone.add_edge(node1_start_best,node2_start_best,length=round(dist_drone[node1_start_best][node2_start_best],2),color=paths_colors[drone_cycle_number])
        visited_list_drone.append(Visited_node_drone(node1_start_best,trip_counter_best))
        visited_list_drone.append(Visited_node_drone(node2_start_best,trip_counter_best))
        cost=compute_drone_cost_new(trip_counter_best)
        weight=compute_drone_weight(trip_counter_best)
        #e blocco l arco del truck
        truck_locked_edges.append([node1_start_best,node2_start_best])


        #ripercorro il ciclo best
        while(cost<=drone_autonomy and weight<=drone_capacity and len(visited_list_indexes)<client_number):
            best_node_index,node1_start_best,node2_start_best=find_best_edge(graph_drone,dist_drone,trip_counter_best)
            #Ora ho trovato il nodo con detour di costo minimo, e i 2 nodi a cui collegarlo
            #quindi lo aggiungo e rimuovo l edge corrispondente SOLO SE NON SUPERO I VINCOLI
            weight=compute_drone_weight(trip_counter_best)+weights_dict[best_node_index]
            new_edge_cost=(dist_drone[best_node_index][node1_start_best]) + (dist_drone[best_node_index][node2_start_best])

            visited_list_truck_indexes=compute_visited_list_truck()
            # se i 2 nodi da rimuovere sono quellindi arrivo e partenza(sonole perocorso del truck) il costo dell arco é zero
            if((node1_start_best in visited_list_truck_indexes and node2_start_best in visited_list_truck_indexes)==False):
                old_edge_cost=dist_drone[node1_start_best][node2_start_best]
            else:
                old_edge_cost=0

            cost_temp=compute_drone_cost_new(trip_counter_best)
            cost=cost_temp-old_edge_cost+new_edge_cost

            if(weight<=drone_capacity and cost<=drone_autonomy):
                graph_drone.add_edge(best_node_index,node1_start_best,length=round(dist_drone[best_node_index][node1_start_best],2),color=paths_colors[drone_cycle_number])
                graph_drone.add_edge(best_node_index,node2_start_best,length=round(dist_drone[best_node_index][node2_start_best],2),color=paths_colors[drone_cycle_number])

                visited_list_indexes=compute_visited_list()
                visited_list_drone.append(Visited_node_drone(best_node_index,trip_counter_best))
                # conto quanti clienti sta servendo il drone in questo viaggio
                visited_list_drone_this_trip=[node.index for node in visited_list_drone if node.trip_number==trip_counter_best]
                sub_clients_counter=len(visited_list_drone_this_trip)
                #lo rimuovo in ogni caso cosi risolvo il rpoblema dell arco obbligatorio
                graph_drone.custom_remove_edge(node1_start_best,node2_start_best)
                cost=compute_drone_cost_new(trip_counter_best)    
                weight=compute_drone_weight(trip_counter_best)


                
    
        return node1_start_best,node2_start_best
    else:
        return -1,-1
    


#Creazione grafi
   
graph_truck_clear=Custom_Graph()
graph_drone_clear=Custom_Graph()   

#----------Inizio lettura coordinate e inserimento nel grafo e distanze drone-------------
#region
filename = 'Posizioni_clienti.txt'      #nome file puntatore
with open(filename, 'r') as f:
    data = f.read()

istance = open(filename, 'r')  
coord_section = False
points = {}
weights_dict = {}

for line in istance.readlines():
    if re.match('START.*', line):
        coord_section = True
        continue
    elif re.match('FINE.*', line):
        break

    if coord_section:                                                 #CREAZIONE GRAFO
        coord = line.split(' ')
        index = int(coord[0])
        coord_x = float(coord[1])
        coord_y = float(coord[2])
        points[index] = (coord_x, coord_y)
        weight= float(coord[3])
        weights_dict[index]=weight
        graph_truck_clear.add_node(index, pos=(coord_x, coord_y))
client_number=index
client_number_range=client_number+1  
istance.close()
graph_truck = graph_truck_clear.copy()  
graph_drone = graph_drone_clear.copy()
#Inizializzo la matrice delle distanze del drone
dist_drone = [ [ 0 for i in range(client_number_range) ] for j in range(client_number_range) ]
#Calcolo le distanze e riempio la matrice del drone
for i in range(1,client_number_range):   
    for j in range(1,client_number_range):
        dist_drone[i][j]=math.sqrt((points[j][0]-points[i][0])**2+(points[j][1]-points[i][1])**2)

#endregion
#----------Inizio Lettura file distanze truck----------------
#region
filename = 'Distanze_TRUCK.txt'      #nome file puntatore
with open(filename, 'r') as f:
    data = f.read()

istance = open(filename, 'r')  
dist_section = False
i=1
dist_truck = [ [ 0 for i in range(client_number_range) ] for j in range(client_number_range) ]
    #Inizio lettura coordinate e inserimento nel grafo
for line in istance.readlines():
    if re.match('START.*', line):
        dist_section=True
        continue
    elif re.match('FINE.*', line):
        break

    #CREAZIONE matrice
    if dist_section:   
        coord = line.split(' ')
        for j in range(0,client_number):
            dist_truck[i][j+1] = float(coord[j])
    i+=1
istance.close()
#endregion
#endregion

#Decido il nodo di partenza, ovvero il nostro deposito. 
starting_node = 29
drone_autonomy = 35
drone_capacity = 300
paths_colors=['red','#7C69FF','#00EB2D','#DDD900','#928017','#A1B1F8','#9DFD83','#8CFF00',\
'#C6FF00','#0040FE','#5B998D','#A36CB1 ','#687044','#B391CB','#27670C']
figure=plt.figure(figsize=(9.5,9.5))
results_dic={}
population=[]

inputs=[w/10 for w in range(-40,-10,5)]+\
    [w/10 for w in range(-10,-5,2)]+\
    [w/10 for w in range(-5,5,1)]+\
    [w/10 for w in range(5,10,2)]+\
    [w/10 for w in range(10,40,5)]
    
ab_list=[]
for alpha in inputs:
    for beta in inputs:
        key1=[alpha,beta]
        ab_list.append(key1)

desc="Trying different values... alpha="+str(inputs[0])+" beta="+str(inputs[0])+"   "
desc_len=len(desc)
pbar=tqdm(ab_list, desc=desc,leave=True,bar_format='{l_bar}{bar:40}{r_bar}{bar:-10b}')
for key in pbar:
    alpha=key[0]
    beta=key[1]
    desc="Trying different values... alpha="+str(alpha)+" beta="+str(beta)+"  "
    while len(desc)!=desc_len:
        if len(desc)<desc_len:
            desc+=" "
        if len(desc)>desc_len:
            desc=desc[:-1]
    pbar.set_description(desc)

    solution=[]
    #rimuovo gli archi creati ai cicli precedenti(parto da un grafo nuovo)
    graph_truck.remove_edges_from(list(graph_truck.edges))
    graph_drone.remove_edges_from(list(graph_drone.edges))

    #Decido il nodo di partenza, ovvero il nostro deposito. 
    truck_node_index = starting_node

    #Dichiaro la lista dei nodi visitati durante l'algoritmo
    visited_list_indexes = [starting_node]
    #Dichiaro la lista dei nodi visitati dal truck durante l'algoritmo
    visited_list_truck_indexes = [starting_node]
    drone_cycle_number=0
    cost = 0    #costo iniziale del veicolo
    drone_on_truck=1


    visited_list_drone=[]
    truck_locked_edges=[]

    # counter per i viaggi dell drone, anche quelli che poi annullo
    drone_trip_counter=0
    

    # conto quanti clienti fa il drone
    drone_clients_counter=0

    #-------FINE INIZIALIZZAZIONE-------


    #INIZIO CODICE
    #Creo la lista con le distanze dei vicini
    neighbors_distance = [0]
    for i in range(1, client_number_range): 
        neighbors_distance.append(dist_drone[truck_node_index][i])
    #Inserisco in nearest_index il nodo più vicino al truck
    nearest_index = nearest_node(neighbors_distance, visited_list_indexes)
    graph_truck.add_edge(truck_node_index,nearest_index,length=round(dist_truck[truck_node_index][nearest_index],2),color='r')
    visited_list_truck_indexes=compute_visited_list_truck()
    visited_list_indexes=compute_visited_list()

    #ciclo esterno del truck
    first_time=1
    last_node=0

    while(len(visited_list_indexes)<client_number):
        sub_clients_counter=0
        drone_returned=False
        #CHEAPEST INSERTION TRUCK
        #controllo se il truck può fare solo un nodo: sono gia ad almeno un nodo, quindi aggiungo l arco piu conveniente    
        best_node_index,node1_best,node2_best=find_best_edge(graph_truck,dist_truck,-1)

        #Ora ho trovato il nodo con detour di costo minimo, e i 2 nodi a cui collegarlo
        #quindi lo aggiungo e rimuovo l edge corrispondente
        graph_truck.add_edge(best_node_index,node1_best,length=round(dist_truck[best_node_index][node1_best],2),color='r')
        graph_truck.add_edge(best_node_index,node2_best,length=round(dist_truck[best_node_index][node2_best],2),color='r')
        visited_list_indexes.append(best_node_index)
        visited_list_truck_indexes=compute_visited_list_truck()
        #rimuovo solo se non sono al 2 ciclo, senno per la storia del undirected eliminerei il primo arco
        if(len(visited_list_truck_indexes)>3):
            graph_truck.custom_remove_edge(node1_best,node2_best)

        
        #CICLO DEL DRONE
        if(len(visited_list_indexes)<client_number):
            drone_cycle_number+=1
            drone_Cheapest_trip()

        cost=compute_solution_cost(dist_truck)


        

    cost=compute_solution_cost(dist_truck)
    #print("Costo=",cost)
    key=str(alpha)+" & "+str(beta)
    results_dic[key]=cost
        
    #Aggiungo alla lista per GA
    truck_path=[]
    nodeA=visited_list_truck_indexes.pop(0)
    truck_path.append(nodeA)
    while(len(visited_list_truck_indexes)>0):
        nodeA_neighbours=[node2 for node1,node2 in graph_truck.edges() if node1==nodeA and node2 not in truck_path]+[node1 for node1,node2 in graph_truck.edges() if node2==nodeA and node1 not in truck_path]
        next_node=nodeA_neighbours[0]
        visited_list_truck_indexes.remove(next_node)
        truck_path.append(next_node)
        nodeA=next_node
        
    solution.append(truck_path)

    trip_counters=[node.trip_number for node  in visited_list_drone]
    trip_counters=list(set(trip_counters))

    
    for trip in trip_counters:
        drone_path=[]
        visited_list_drone_this_trip=[node.index for node in visited_list_drone if node.trip_number==trip]
        nodeA=visited_list_drone_this_trip.pop(0)
        drone_path.append(nodeA)
        while(len(visited_list_drone_this_trip)>0):
            nodeA_neighbours=[node2 for node1,node2 in graph_drone.edges() if node1==nodeA and node2 in visited_list_drone_this_trip and node2 not in drone_path]+\
                [node1 for node1,node2 in graph_drone.edges() if node2==nodeA and node1 in visited_list_drone_this_trip and node1 not in drone_path]

            next_node=nodeA_neighbours[0]
            visited_list_drone_this_trip.remove(next_node)
            drone_path.append(next_node)
            nodeA=next_node
        solution.append(drone_path)
    
    #riempio di spazi vuoti
    while(len(solution)<15):
        solution.append([])

    population.append(solution)

key_migliore=min(results_dic, key = lambda k: results_dic[k])
migliore_valore=results_dic[key_migliore]

        
#scrivo su file i risultati
with open('GA_input.txt', 'w') as GA_input:
    GA_input.writelines(str(starting_node)+"\n")
    GA_input.writelines(str(drone_autonomy)+"\n")
    GA_input.writelines(str(drone_capacity)+"\n")
    json.dump(population, GA_input)




with open('aaaaa.txt', 'w') as aaa:
    for key, value in results_dic.items():
        aaa.write(str(key)+ " : "+str( value)+"\n")

print("Nodo iniziale=",starting_node)
print("Autonomia drone", drone_autonomy)
print("Capacita", drone_capacity)
print(key_migliore,"ha dato un costo di",migliore_valore)

end = time.time()
print(end - start, "secs")
i=0
for key, value in results_dic.items():
    if key==key_migliore:
        k=i
        break     
    i+=1  

sol=population[i]

with open('2_OPT_input.txt', 'w') as Two_opt_input:
    Two_opt_input.writelines(str(starting_node)+"\n")
    Two_opt_input.writelines(str(drone_autonomy)+"\n")
    Two_opt_input.writelines(str(drone_capacity)+"\n")
    json.dump(sol, Two_opt_input)
cost=compute_solution_cost(dist_truck)

solution_to_print = []
for element in sol:
    if element != []:
        solution_to_print.append(element)
    else:
        continue
print("La soluzione al problema con L'algoritmo Cheapest Insertion è --> ", solution_to_print, "\n")
for path in solution_to_print:
    if path == solution_to_print[0]:
        print("Dove il truck percorre la seguente route --> ", path, "\n")
    elif path == solution_to_print[1]:
        print("Mentre il drone percorre le seguenti routes:\n", path)
    else: 
        print(path)
#print("Costo=",cost)
print_graph_for_debugs(sol)




