# Federated Learning Project

This repo contains the Server, Node and middleware code for the Federated Learning Project.

In order to run the components:
- Ensure docker is installed
- Install server requirements.txt to a virtual environment (venv). Insert the FLM package into the venv python path.
- Insert the data into a top level /data/ folder. 
- Run build_nodes.py in place.
- Run the server using the venv. Ensure that the server is waiting for the correct number of nodes.
- Run the launch_nodes.sh script.

Brief description of components:
- FLM (Middleware): This middleware is built on top of python sockets with pickle and custom serialisation. It is designed for use with the MessageDefinitions found inside.
- Node (Client): This node is designed for running with docker, though can be run outside a container with the correct flags passed. Each node must have a different, new working directory if this is the case
- Server: This is designed to be run on desktop

## Middleware
The middleware package is designed around the session manager classes. Users of the middleware only have to create an instance of the corresponding session manager, and pass messages from the MessageDefinitions.\
Also included in the middleware is the checkpoint handler, which is a tensorflow-specific implementation which enables the user to save models to be sent using the middleware.

## Node
The nodes are designed to be run inside docker containers, in order to completely isolate them. They only need to be started and will perform a round of training automatically, given they can make a connection to the server.\
In order to build the node image, data must be provided.

Flags:
- --run_on_dekstop_extension: the node-specific extension to the base path to avoid conflicts running the node multiple times on the same machine


## Server
The server is the controller of the training. It is designed to be run on desktop. With the command line arguments specified, it will complete a round of training, given that it can gather the number of nodes specified.

Flags:
- --local_port [port]: the local port to listen for nodes on. Should only be used if the nodes are also configured to connect to a specific port
- --node_count [number]: the number of nodes to gather before a round of training can be completed
- --epochs [number]: the number of epochs of training to be completed by the nodes
- --training_timeout [timeout]: the number of seconds the server should wait before dropping nodes from training
- --rm: if specified, the server will delete all runtime files after the round is completed, and will not use a saved model
- --plot: if specified, the server will plot training graphs to view