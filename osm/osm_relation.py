class OsmRelation:
    def __init__(self, id, colour, name, network, operator,
                 from_, to, ref, route, wheelchair):
        self.id = id
        self.colour = colour
        self.name = name
        self.network = network
        self.operator = operator
        self.from_ = from_
        self.to = to
        self.ref = ref
        self.route = route
        self.wheelchair = wheelchair
    
    def add_relation_id(self, id):
        self.relation_ids.append(id)
    
    def add_way_id(self, id):
        self.way_ids.append(id)
    
    def add_node_id(self, id):
        self.node_ids.append(id)
    
    def add_relation(self, relation):
        self.relations.append(relation)
    
    def add_way(self, relation):
        self.ways.append(relation)
    
    def add_node(self, node):
        self.nodes.append(node)