import zmq
from unified_planning.grpc.proto_writer import ProtobufWriter

class PlanPublisher:
    """
    Publishes Unified Planning Problem and Plan objects to a ZeroMQ topic
    using the UP Protobuf format.
    """
    def __init__(self, host='*', port=5555, topic='robot_plan'):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        try:
            self.socket.bind(f"tcp://{host}:{port}")
            print(f"[PlanPublisher] Bound to tcp://{host}:{port}, topic: '{topic}'")
        except zmq.ZMQError as e:
            print(f"[PlanPublisher] Error binding to port {port}: {e}")
            
        self.topic = topic.encode('utf-8')
        self.writer = ProtobufWriter()

    def publish(self, problem, plan):
        """
        Serializes and publishes the problem and plan.
        Message format (Multipart):
        [Topic, Problem_Protobuf_Bytes, Plan_Protobuf_Bytes]
        """
        if plan is None:
            print("[PlanPublisher] Plan is None, skipping publish.")
            return

        try:
            # Convert to Protobuf
            proto_problem = self.writer.convert(problem)
            proto_plan = self.writer.convert(plan)
            
            # Serialize to bytes
            problem_bytes = proto_problem.SerializeToString()
            plan_bytes = proto_plan.SerializeToString()
            
            # Send multipart message
            self.socket.send_multipart([self.topic, problem_bytes, plan_bytes])
            print(f"[PlanPublisher] Published problem ({len(problem_bytes)} bytes) and plan ({len(plan_bytes)} bytes).")
            
        except Exception as e:
            print(f"[PlanPublisher] Failed to publish: {e}")

    def close(self):
        self.socket.close()
        self.context.term()
