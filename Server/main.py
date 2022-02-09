import FLServer
import ServerTensorflowHandler
import DataWrapper

if __name__ == '__main__':
    data_wrapper = DataWrapper.DataWrapper("/home/max/Documents/FederatedLearning/Data/data.csv")
    tensorflow_handler = \
        ServerTensorflowHandler.TensorflowHandler("BasicHandler", data_wrapper)
    server = FLServer.FLServer("LocalServer", tensorflow_handler)
    server.run_server()
