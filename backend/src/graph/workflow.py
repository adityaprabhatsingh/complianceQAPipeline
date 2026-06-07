'''
This module define the DAG(directed Acyclic graph) that orchestrates the video compinaces audit process

it connect the node using stategraph from langchain

START ->  index_video_node -> audit_content_node ->END



'''

from langgraph.graph import StateGraph,END
#stategraph create a workflow graph
# it define the ending point
from backend.src.graph.state import VideoAuditState
from backend.src.graph.nodes import (
    index_video_node,
    audit_content_node
)


def create_graph():
    '''
    This function builds the entire DAG workflow.
    Contruct and compile the Langgraph workflow
    return:
    compliled graph :runnable graph object for excecution 
    '''

    #initialed the graph with state schema
    # it tell the it must accept and return the data that match the videoauditstate structue if somerandom it show error  
    workflow = StateGraph(VideoAuditState)

    # add a node
    workflow.add_node('indexer',index_video_node)
    workflow.add_node('auditor',audit_content_node)
    
    #define the entry point: indexer

    workflow.set_entry_point('indexer')

    #define edges 
    workflow.add_edge('indexer','auditor')

    #once the auditor completed teh eorkflow come to end

    workflow.add_edge('auditor',END)


    # complele the graph
    #it freeze the data and convert to a runnable application 
    # .complile check the error and check the disconnected node like a work of complier 
    app=workflow.compile()
    return app


#expose this runnable graph 
app=create_graph()





#



