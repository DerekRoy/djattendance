from ortools.graph import pywrapgraph
from sets import Set
import random

class DirectedFlowGraph:
  # source, sink, nodes, adj, ortool_graph

  # obj: index


  STATUS = {
     0:   'NOT_SOLVED',
     1:   'OPTIMAL',
     2:   'FEASIBLE',
     3:   'INFEASIBLE',
     4:   'UNBALANCED',
     5:   'BAD_RESULT',
     6:   'BAD_COST_RANGE'
  }


  nodes = {}

  # stages[1] = Set([node])
  stages = {}
  # (fromIndex, toIndex): (capacity, cost)
  # adj[u][v] = (capacity, cost)
  adj = {}
  # total_flow to flow through whole graph
  total_flow = 0


  def __len__(self):
    return len(self.nodes)

  def __getitem__(self, n):
    return self.adj[n]

  def __contains__(self, n):
    try:
      return n in self.nodes
    except TypeError:
      return False

  def __iter__(self):
    return iter(self.nodes)

  # def copy(self):
  #   from copy import deepcopy
  #   return deepcopy(self)

  def set_total_flow(self, flow):
    self.total_flow = flow

  def get_stage(self, stage):
    # Return stages[stage] if exists or else Set()
    return self.stages.get(stage, Set())

  def get_node_index(self, node, stage=1):
    if node not in self.nodes:
      self.nodes[node] = len(self.nodes)
      # Keep track of node stages
      st = self.stages.setdefault(stage, Set())
      st.add(node)

    return self.nodes[node]

  def add_or_set_arc(self, fro, to, capacity=1, cost=1, stage=1):
    fi = self.get_node_index(fro, stage)
    ti = self.get_node_index(to, stage + 1)

    # Get fi if exists if not create a new dict for that key and return it
    edges = self.adj.setdefault(fi, dict())
    edges[ti] = (capacity, cost)

  def remove_arc(self, u, v):
    try:
      del self.adj[u][v]
    except KeyError:
      raise Exception("The edge %s-%s is not in the graph" % (u, v))


  def get_arc(self, fro, to):
    if fro in self.adj and to in self.adj[fro]:
      return self.adj[fro][to]
    else:
      return None

  def print_arcs(self):
    for fro in self.adj:
      for to in self.adj[fro]:
        capacity, cost = self.adj[fro][to]
        print 'Edge %s -> %s : %d, %d' % (str(fro), str(to), capacity, cost)

  def print_stages(self):
    stages = self.stages.keys()
    stages.sort()

    ns = []

    for i in stages:
      st = self.stages[i]
      print 'stage %d : %s' % (i, str(st))

  # Compile into a ORTOOLS graph for faster calculations in C
  def compile(self):
    if self.total_flow <= 0:
      raise Exception('You forgot to set a positive total flow!')

    min_cost_flow = pywrapgraph.SimpleMinCostFlow()

    for fro in self.adj:
      for to in self.adj[fro]:
        capacity, cost = self.adj[fro][to]
        min_cost_flow.AddArcWithCapacityAndUnitCost(fro, to, capacity, cost)

    # Set flow for source/sink. Get first and last stage as source/sink
    st = self.stages
    ks = st.keys()
    ks.sort()
    (source, ) = st[ks[0]]
    (sink, ) = st[ks[-1]]
    source, sink = self.nodes[source], self.nodes[sink]
    print 'source/sink/flow', source, sink, self.total_flow
    min_cost_flow.SetNodeSupply(source, self.total_flow)
    min_cost_flow.SetNodeSupply(sink, -self.total_flow)


    self.ortool_graph = min_cost_flow

    return min_cost_flow

  def print_solution(self):
    self.soln = []

    g = self.ortool_graph

    if self.status == g.OPTIMAL:
      print 'Total flow cost', g.OptimalCost()
      print 'Total max flow', g.MaximumFlow()
      print 'Total # of nodes', g.NumNodes()
      print 'Total # of edges', g.NumArcs()
      for i in range(0, g.NumArcs()):
        if g.Flow(i) > 0:
          self.soln.append([g.Tail(i), g.Head(i)])
          print 'From source %d to target %d: cost %d' % (
              g.Tail(i),
              g.Head(i),
              g.UnitCost(i))
          self.graph()
    else:
      print 'There was an issue with the min cost flow input.', self.status, self.STATUS[self.status]


  # Solve with max partial flow allowed in graph
  def solve_partial_flow(self):
    self.compile()
    self.status = self.ortool_graph.SolveMaxFlowWithMinCost()

    self.print_solution()

  # solve graph for Full flow: compile() first and then .solve()
  def solve(self):
    self.compile()

    self.status = self.ortool_graph.Solve()

    self.print_solution()

    
  def graph(self):
    filename = '/home/rayli/Desktop/data.js'
    f = open(filename,'w')
    # print >>f, 'whatever'

    ########### js stuff!

    js_edges = []
    for fro in self.adj:
      for to in self.adj[fro]:
        capacity, cost = self.adj[fro][to]
        js_edges.append({'source': fro, 'target': to, 'weight': cost})


    constraints = []
    # loop through all the stages in order and create column constraints for each
    stages = self.stages.keys()
    stages.sort()

    ns = []

    max_stage_length = 0

    for i in stages:
      st = self.stages[i]
      if len(st) > max_stage_length:
        max_stage_length = len(st)

      st_constraint = []

      st_ns = []
      # iterating through a set
      for n in st:
        index = self.nodes[n]
        st_constraint.append({"node":str(index), "offset":"0"})

        st_ns.append(index)

      constraints.append({"type": "alignment", "axis":"x", "offsets": st_constraint})

      ns.append(st_ns)




    code = '''
var color = ["#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c", "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5", "#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f", "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5"];
var st_ns = %s;
var ns = [];
var n_tot = %d;
var scaling = 40;
var X_OFFSET = 200;
var MARGIN = 100;
var max_stage_length = %d;

// source/sink
//ns.push({id: 0, fixed: true, x: 100, y: services * scaling});
//ns.push({id: n_tot - 1, fixed: true, x: 500, y: services * scaling});

for (var i in st_ns) {
  // In stage i nodes
  var ns_i = st_ns[i];
  var Y_OFFSET = (max_stage_length - ns_i.length) / 2;
  for (var j in ns_i) {
    var n = ns_i[j];
    ns.push({id: n, fixed: true, x: MARGIN + i * X_OFFSET, y: MARGIN + (Y_OFFSET + parseInt(j)) * scaling});
  }
}
''' % (str(ns), self.ortool_graph.NumNodes(), max_stage_length)

    f.write(code)
    # print >>f code
    f.write('constraints = ' + str(constraints) + '\n')
    f.write('lks = ' + str(js_edges) + '\n')
    f.write('solns = ' + str(self.soln) + '\n')
 

# Test stuff

def serviceMinCostFlow():

  # Don't make services same as trainees!
  services = 4
  trainees = 6
  s_t_ratio = services / (trainees - 1)
  # number of services per trainee
  t_s_max_capacity = 2
  expected_cost = 275

  # service/trainee labels
  s_l = 'service_'
  t_l = 'trainee_'

  ss_edges = [] # Source to service
  st_edges = [] # Service to Trainee
  tt_edges = [] # Trainee to sink t

  pos = {}
  s_nodes = []
  t_nodes = []


  pos['s'] = [0, services / 2]

  # Edge Count
  e_count = 0

  # G = nx.DiGraph()
  # # source
  # G.add_node('s', demand = -services)
  # # sink node
  # G.add_node('t', demand = services)


  '''
    ArcIndex AddArcWithCapacityAndUnitCost(NodeIndex tail, NodeIndex head,
                                           FlowQuantity capacity,
                                           CostValue unit_cost);
  '''

  node_count = 0;

  min_cost_flow = DirectedFlowGraph()

  # Add services to source
  for i in range(services):
    node_count += 1
    (fro, to) = (0, node_count)
    ss_edges.append((fro, to, 1))
    pos[to] = [1, i]
    s_nodes.append(to)
    min_cost_flow.add_or_set_arc(fro, to, 1, 1, 1)
    # G.add_edge(fro, to, weight = 1, capacity = 1, edge_color='g')
    e_count+=1

  # Add trainees to services
  for i in range(trainees):
    node_count += 1 
    for j in range(1, services + 1):
      # flip a coin to determine to link the trainee to services or not. 3/4 change of linkage
      if random.random() <= 0.75:
        (fro, to) = (j, node_count)
        cost = random.randint(1, 10)
        st_edges.append((fro, to, cost))
        min_cost_flow.add_or_set_arc(fro, to, 1, cost, 2)
        # G.add_edge(fro, to, weight = random.randint(1, 10), capacity = 1, edge_color='r')
        e_count+=1

  print 'node_count, sink', node_count + 1
  # add trainees all to sink t
  for j in range(trainees):
    (fro, to) = (node_count - j, node_count + 1)
    pos[fro] = [2, s_t_ratio * j]
    t_nodes.append(fro)
    num_services = random.randint(1, 3)
    sick_lvl = random.randint(1, 10)
    for x in range(1, t_s_max_capacity + 1):
      tt_edges.append((fro, to, x * sick_lvl))
      min_cost_flow.add_or_set_arc(fro, to, 1, x * sick_lvl, 3)
    # G.add_edge(fro, to, weight = random.randint(1, 3), capacity = t_s_max_capacity, edge_color='b')
    e_count+=1

  # min_cost_flow.SetNodeSupply(0, services)
  # min_cost_flow.SetNodeSupply(node_count + 1, -services)

  min_cost_flow.set_total_flow(services)

  # print 'edges', min_cost_flow.adj

  min_cost_flow.print_arcs()

  min_cost_flow.print_stages()

  min_cost_flow.solve()






serviceMinCostFlow()