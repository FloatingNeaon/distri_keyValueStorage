import grpc
from concurrent import futures
import keyvaluestore_pb2
import keyvaluestore_pb2_grpc

# 实现键值存储服务
class KeyValueStoreServicer(keyvaluestore_pb2_grpc.KeyValueStoreServicer):
    def __init__(self):
        self.datastore = {}
        self.locks = {}  # 存储锁

    def AcquireLock(self, request, context):
        lock_key = request.key

        lock = True
        
        if lock_key not in self.locks:  
            self.locks[lock_key] = lock  # 将锁存储到字典中
            return keyvaluestore_pb2.LockResponse(lock_acquired=True)
        else:
            return keyvaluestore_pb2.LockResponse(lock_acquired=False)

    def ReleaseLock(self, request, context):
        lock_key = request.key

        # 释放分布式锁
        if lock_key in self.locks:
            del self.locks[lock_key]

        return keyvaluestore_pb2.LockResponse(lock_acquired=False)

    def Put(self, request, context):
        lock_key = request.key

        if lock_key in self.locks:  # 使用锁来保护对存储的访问
            self.datastore[request.key] = request.value
            return keyvaluestore_pb2.Response(message=f'Key "{request.key}" stored successfully.')
        else:
            return keyvaluestore_pb2.Response(message=f'Failed to store key "{request.key}". Lock not acquired.')

    def Get(self, request, context):
        lock_key = request.key

        if lock_key in self.locks: # 使用锁来保护对存储的访问
            if request.key in self.datastore:
                return keyvaluestore_pb2.Response(message=f'The value is "{self.datastore[request.key]}".')
            else:
                return keyvaluestore_pb2.Response(message=f'Cannot find key "{request.key}" in system".')
        else:
            return keyvaluestore_pb2.Response(message=f'Failed to get value. Lock not acquired.')

    def Delete(self, request, context):
        lock_key = request.key

        if lock_key in self.locks:  # 使用锁来保护对存储的访问
            if request.key in self.datastore:
                del self.datastore[request.key]
                return keyvaluestore_pb2.Response(message=f'Key "{request.key}" deleted successfully.')
            else:
                return keyvaluestore_pb2.Response(message=f'Key "{request.key}" not found.')
        else :
            return keyvaluestore_pb2.Response(message=f'Failed to delete. Lock not acquired.')
# 启动 gRPC 服务器
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    keyvaluestore_pb2_grpc.add_KeyValueStoreServicer_to_server(KeyValueStoreServicer(), server)
    server.add_insecure_port('[::]:8000')
    server.start()
    print("Server listening on [::]:8000...")
    server.wait_for_termination()

serve()