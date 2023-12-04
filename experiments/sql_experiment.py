from graphviz import Digraph

# Define the steps in your query plan with more concise descriptions
plan_steps = [
    ("SCAN c", "Scan 'customers' for USA."),
    ("SEARCH i", "Search 'invoices' using index on CustomerId."),
    ("SEARCH ii", "Search 'invoice_items' using index on InvoiceId."),
    ("SEARCH t", "Search 'tracks' using primary key."),
    ("SEARCH g", "Search 'genres' using primary key."),
    ("GROUP BY", "Group by genre using B-tree."),
    ("ORDER BY", "Order by total sales using B-tree.")
]

def visualize_query_plan(plan_steps):
    dot = Digraph(comment='SQL Query Plan', graph_attr={'rankdir': 'TB', 'pad': '0.5'}, node_attr={'shape': 'box', 'style': 'filled', 'fillcolor': 'lightgrey', 'height': '0.6'})
    # dot.attr(size='8,5')

    # Adding nodes
    dot.node('start', 'Start', shape='ellipse', fillcolor='darkolivegreen1')
    dot.node('end', 'End', shape='ellipse', fillcolor='darkolivegreen1')

    previous_step = 'start'
    for step_id, (step, desc) in enumerate(plan_steps, start=1):
        node_id = f'step{step_id}'
        dot.node(node_id, f'{desc}', shape='box')
        dot.edge(previous_step, node_id)
        previous_step = node_id

    dot.edge(previous_step, 'end')

    # Save and render the graph
    filename = 'query_plan_better'
    dot.render(filename, format='png', cleanup=True)
    return filename + '.png'

# Visualize the query plan with better aesthetics and concise text
visualize_query_plan(plan_steps)
