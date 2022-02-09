import FLServer
import ServerTensorflowHandler

if __name__ == '__main__':
    tensorflow_handler = ServerTensorflowHandler.ServerTensorflowHandler("BasicHandler")
    server = FLServer.FLServer("LocalServer", tensorflow_handler)
    server.run_server()
