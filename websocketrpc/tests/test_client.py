from websocketrpc import Client

class TestClient(Client):
    pass

def main():
    TestClient.parse_args_and_run()

if __name__=='__main__':
    main()
