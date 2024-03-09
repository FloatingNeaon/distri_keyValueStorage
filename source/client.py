import grpc
import keyvaluestore_pb2
import keyvaluestore_pb2_grpc

def run():
    # 连接到服务器
    channel = grpc.insecure_channel('localhost:8000')
    stub = keyvaluestore_pb2_grpc.KeyValueStoreStub(channel)

    # 在客户端使用键值存储
    while True:

        print("Please input the operation you want:")
        operation = input()

        # 键值对添加/修改
        if operation == "PUT" or operation == "put":
            key_input = input("Please input the Key:\n")
            
            # 请求获取锁
            lock_response = stub.AcquireLock(keyvaluestore_pb2.LockRequest(key=key_input))
            if lock_response.lock_acquired:
                value_input = input("Please input the Value you want to match:\n")
                put_response = stub.Put(keyvaluestore_pb2.Request(key=key_input, value=value_input))
                print(put_response.message)
                lock_release_mes = stub.ReleaseLock(keyvaluestore_pb2.Request(key=key_input))  # 释放分布式锁
            else:
                print("Failed to acquire lock. Another client is currently accessing the key.")

        # 键值读取
        elif  operation == "GET" or operation == "get":
            key_input = input("Please input the Key you want to search:\n")
            lock_response = stub.AcquireLock(keyvaluestore_pb2.LockRequest(key=key_input))
            if lock_response.lock_acquired:
                get_response = stub.Get(keyvaluestore_pb2.Request(key=key_input))
                print(get_response.message)
                lock_release_mes = stub.ReleaseLock(keyvaluestore_pb2.Request(key=key_input))  # 释放分布式锁
            else:
                print("Failed to acquire lock. Another client is currently accessing the key.")

        # 键值对删除
        elif operation == "DEL" or operation == "del":
            key_input = input("Please input the Key you want to delete from the system:\n")
            lock_response = stub.AcquireLock(keyvaluestore_pb2.LockRequest(key=key_input))
            if lock_response.lock_acquired:
                delete_response = stub.Delete(keyvaluestore_pb2.Request(key=key_input))
                print(delete_response.message)
                lock_release_mes = stub.ReleaseLock(keyvaluestore_pb2.Request(key=key_input))  # 释放分布式锁
            else:
                print("Failed to acquire lock. Another client is currently accessing the key.")

        # 结束客户端进程
        elif operation == "QUIT" or operation == "EXIT" \
            or operation == "q" or operation == "quit" or operation == "exit":
            print("Thanks for using, goodbye!")
            break

        # 非法输入
        else:
            print("Unknown command, please retry:")
            continue

run()