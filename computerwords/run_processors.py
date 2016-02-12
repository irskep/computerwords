from processors import get_processor, process_node

def run_processors(node_store):
    # THIS DOESN'T WORK IF YOU MUTATE THE STORE! FIX IT!
    for node in node_store.iterate_preorder():
        process_node(node_store, node)
    return node_store
