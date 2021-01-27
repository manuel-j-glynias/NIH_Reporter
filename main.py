import util


def init_server(name):
    server = name
    util.initialize_graph(server)



#  use "pip install -r requirements.txt" to get required modules
if __name__ == '__main__':
    init_server('localhost')

